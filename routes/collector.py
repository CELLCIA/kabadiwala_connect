from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Lot, Material, Price, Offer, Transaction
import os
from werkzeug.utils import secure_filename
from datetime import datetime

collector_bp = Blueprint('collector', __name__)

@collector_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'collector':
        return redirect(url_for('main.index'))
    lots = Lot.query.filter_by(collector_id=current_user.id).order_by(Lot.created_at.desc()).limit(5).all()
    # Simple stats
    total_lots = Lot.query.filter_by(collector_id=current_user.id).count()
    return render_template('collector/dashboard.html', lots=lots, total_lots=total_lots)

@collector_bp.route('/create_lot', methods=['GET', 'POST'])
@login_required
def create_lot():
    if current_user.role != 'collector':
        return redirect(url_for('main.index'))
    materials = Material.query.all()
    
    if request.method == 'POST':
        material_id = request.form.get('material_id')
        weight = float(request.form.get('weight'))
        condition = request.form.get('condition')
        
        # Handle file upload
        photo = request.files.get('photo')
        filename = None
        if photo and photo.filename != '':
            from flask import current_app
            filename = secure_filename(photo.filename)
            # Create a unique filename
            filename = f"{current_user.id}_{int(datetime.utcnow().timestamp())}_{filename}"
            photo.save(os.path.join(current_app.config['UPLOAD_FOLDER'], 'materials', filename))
            
        # Get current price to estimate value
        price_record = Price.query.filter_by(material_id=material_id).order_by(Price.updated_at.desc()).first()
        estimated_value = weight * price_record.price if price_record else 0

        lot = Lot(
            collector_id=current_user.id,
            material_id=material_id,
            weight=weight,
            condition=condition,
            photo_filename=filename,
            estimated_value=estimated_value,
            status='SUBMITTED'
        )
        db.session.add(lot)
        db.session.commit()
        flash(f'Scrap lot created successfully! Estimated Value: ₹{estimated_value}', 'success')
        return redirect(url_for('collector.dashboard'))
        
    return render_template('collector/create_lot.html', materials=materials)

@collector_bp.route('/price_board')
@login_required
def price_board():
    prices = Price.query.join(Material).all()
    return render_template('collector/price_board.html', prices=prices)

@collector_bp.route('/transactions')
@login_required
def transactions():
    if current_user.role != 'collector':
        return redirect(url_for('main.index'))
    # Only show lots with an associated transaction
    transactions = Transaction.query.join(Lot).filter(Lot.collector_id == current_user.id).order_by(Transaction.updated_at.desc()).all()
    return render_template('collector/transactions.html', transactions=transactions)

@collector_bp.route('/earnings')
@login_required
def earnings():
    if current_user.role != 'collector':
        return redirect(url_for('main.index'))
    
    transactions = Transaction.query.join(Lot).filter(Lot.collector_id == current_user.id).order_by(Transaction.updated_at.desc()).all()
    
    total_earnings = sum(t.final_price for t in transactions if t.payment_status == 'PAID' and t.final_price)
    paid = total_earnings
    pending = sum(t.final_price for t in transactions if t.payment_status != 'PAID' and t.final_price)
    
    # Calculate this month's earnings
    import datetime
    current_month = datetime.datetime.utcnow().month
    current_year = datetime.datetime.utcnow().year
    
    this_month = sum(t.final_price for t in transactions 
                     if t.payment_status == 'PAID' and t.final_price 
                     and t.updated_at.month == current_month 
                     and t.updated_at.year == current_year)
                     
    return render_template('collector/earnings.html', 
                           transactions=transactions, 
                           total_earnings=total_earnings,
                           paid=paid,
                           pending=pending,
                           this_month=this_month)

@collector_bp.route('/lot/<int:lot_id>')
@login_required
def lot_detail(lot_id):
    if current_user.role != 'collector':
        return redirect(url_for('main.index'))
    lot = Lot.query.get_or_404(lot_id)
    if lot.collector_id != current_user.id:
        return redirect(url_for('main.index'))
    return render_template('collector/lot_detail.html', lot=lot)

@collector_bp.route('/lot/<int:lot_id>/find_recyclers')
@login_required
def find_recyclers(lot_id):
    if current_user.role != 'collector':
        return redirect(url_for('main.index'))
    lot = Lot.query.get_or_404(lot_id)
    if lot.collector_id != current_user.id:
        return redirect(url_for('main.index'))
        
    # Match Recyclers:
    # Rule 1: Verified
    # Rule 2: Accepts the material (simple string search for hackathon)
    from models import User
    material_keyword = lot.material.name.split(' ')[0] # e.g. "Printed", "Copper"
    
    # We will just fetch verified recyclers and do matching in python for simplicity
    all_verified = User.query.filter_by(role='recycler', is_verified=True).all()
    
    matched_recyclers = []
    for r in all_verified:
        if r.materials_accepted and material_keyword.lower() in r.materials_accepted.lower():
            matched_recyclers.append(r)
            
    # If string match fails, just show all verified as fallback so it works for demo
    if not matched_recyclers:
        matched_recyclers = all_verified
        
    return render_template('collector/find_recyclers.html', lot=lot, recyclers=matched_recyclers)

@collector_bp.route('/safety')
@login_required
def safety():
    return render_template('collector/safety.html')
