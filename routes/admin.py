import csv
import io
from flask import Blueprint, render_template, redirect, url_for, Response, request, flash
from flask_login import login_required, current_user
from models import db, User, Lot, Transaction, Material, Price, Traceability
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))
    
    total_collectors = User.query.filter_by(role='collector').count()
    total_recyclers = User.query.filter_by(role='recycler').count()
    verified_recyclers = User.query.filter_by(role='recycler', is_verified=True).count()
    total_lots = Lot.query.count()
    active_transactions = Transaction.query.filter(Transaction.status.notin_(['COMPLETED', 'CANCELLED', 'REJECTED'])).count()
    completed_transactions = Transaction.query.filter_by(status='COMPLETED').count()
    
    # Weight and value
    total_weight = db.session.query(func.sum(Lot.weight)).scalar() or 0
    total_value = db.session.query(func.sum(Transaction.final_price)).scalar() or 0
    paid_value = db.session.query(func.sum(Transaction.final_price)).filter(Transaction.payment_status == 'PAID').scalar() or 0
    pending_value = total_value - paid_value

    # Chart data - Material Distribution
    material_stats = db.session.query(Material.name, func.count(Lot.id)).outerjoin(Lot).group_by(Material.id).all()
    mat_labels = [m[0] for m in material_stats]
    mat_data = [m[1] for m in material_stats]

    return render_template('admin/dashboard.html', 
                           c_count=total_collectors, 
                           r_count=total_recyclers, 
                           v_r_count=verified_recyclers,
                           l_count=total_lots,
                           a_tx_count=active_transactions,
                           c_tx_count=completed_transactions,
                           t_weight=total_weight,
                           t_val=total_value,
                           p_val=paid_value,
                           pend_val=pending_value,
                           mat_labels=mat_labels,
                           mat_data=mat_data)

@admin_bp.route('/manage_users')
@login_required
def manage_users():
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))
    users = User.query.filter(User.role != 'admin').all()
    return render_template('admin/manage_users.html', users=users)

@admin_bp.route('/verify_recyclers', methods=['GET', 'POST'])
@login_required
def verify_recyclers():
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        action = request.form.get('action')
        user = User.query.get(user_id)
        if user and user.role == 'recycler':
            if action == 'verify':
                user.is_verified = True
                flash(f'{user.name} verified successfully.', 'success')
            elif action == 'reject':
                user.is_verified = False
                flash(f'{user.name} verification removed/rejected.', 'warning')
            db.session.commit()
            
    recyclers = User.query.filter_by(role='recycler').all()
    return render_template('admin/verify_recyclers.html', recyclers=recyclers)

@admin_bp.route('/manage_prices', methods=['GET', 'POST'])
@login_required
def manage_prices():
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        mat_id = request.form.get('material_id')
        new_price_val = float(request.form.get('price'))
        
        # We don't overwrite, we create a new price record for history
        new_price = Price(material_id=mat_id, price=new_price_val, unit='kg')
        db.session.add(new_price)
        db.session.commit()
        flash('Price updated successfully.', 'success')
        return redirect(url_for('admin.manage_prices'))
        
    materials = Material.query.all()
    # Get latest price for each material
    latest_prices = []
    for m in materials:
        p = Price.query.filter_by(material_id=m.id).order_by(Price.updated_at.desc()).first()
        latest_prices.append({'material': m, 'price': p})
        
    return render_template('admin/manage_prices.html', materials=materials, latest_prices=latest_prices)

@admin_bp.route('/export/<dataset>')
@login_required
def export_data(dataset):
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))
        
    output = io.StringIO()
    writer = csv.writer(output)
    
    if dataset == 'collectors':
        writer.writerow(['ID', 'Name', 'Email', 'Location', 'Language'])
        for c in User.query.filter_by(role='collector').all():
            writer.writerow([c.id, c.name, c.email, c.location, c.preferred_language])
            
    elif dataset == 'recyclers':
        writer.writerow(['ID', 'Name', 'Location', 'Materials Accepted', 'Verified'])
        for r in User.query.filter_by(role='recycler').all():
            writer.writerow([r.id, r.name, r.location, r.materials_accepted, r.is_verified])
            
    elif dataset == 'transactions':
        writer.writerow(['ID', 'Lot ID', 'Collector ID', 'Recycler ID', 'Final Price', 'Status', 'Payment Status', 'Date'])
        for t in Transaction.query.all():
            writer.writerow([t.id, t.lot_id, t.lot.collector_id, t.recycler_id, t.final_price, t.status, t.payment_status, t.created_at])
            
    elif dataset == 'traceability':
        writer.writerow(['ID', 'Transaction ID', 'Event', 'Actor ID', 'Timestamp'])
        for tr in Traceability.query.all():
            writer.writerow([tr.id, tr.transaction_id, tr.event, tr.actor_id, tr.timestamp])
            
    output.seek(0)
    return Response(output.getvalue(), mimetype='text/csv', headers={"Content-Disposition": f"attachment;filename={dataset}.csv"})
