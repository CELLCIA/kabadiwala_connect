from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Lot, Offer, Transaction

recycler_bp = Blueprint('recycler', __name__)

@recycler_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'recycler':
        return redirect(url_for('main.index'))
        
    # Incoming lots (not accepted by anyone yet)
    available_lots = Lot.query.filter(Lot.status.in_(['SUBMITTED', 'OFFER_RECEIVED'])).order_by(Lot.created_at.desc()).all()
    my_offers = Offer.query.filter_by(recycler_id=current_user.id).all()
    
    # Active transactions (not COMPLETED/CANCELLED)
    active_transactions = Transaction.query.filter(
        Transaction.recycler_id == current_user.id,
        Transaction.status.notin_(['COMPLETED', 'CANCELLED', 'REJECTED'])
    ).order_by(Transaction.updated_at.desc()).all()
    
    # Completed transactions
    completed_transactions = Transaction.query.filter_by(
        recycler_id=current_user.id, 
        status='COMPLETED'
    ).order_by(Transaction.updated_at.desc()).all()
    
    return render_template('recycler/dashboard.html', 
                           lots=available_lots, 
                           offers=my_offers,
                           active_transactions=active_transactions,
                           completed_transactions=completed_transactions)

@recycler_bp.route('/make_offer/<int:lot_id>', methods=['POST'])
@login_required
def make_offer(lot_id):
    if current_user.role != 'recycler':
        return redirect(url_for('main.index'))
        
    price = float(request.form.get('price_per_kg'))
    pickup = True if request.form.get('pickup_available') else False
    
    offer = Offer(
        lot_id=lot_id,
        recycler_id=current_user.id,
        price_per_kg=price,
        pickup_available=pickup
    )
    
    lot = Lot.query.get_or_404(lot_id)
    lot.status = 'OFFER_RECEIVED'
    
    db.session.add(offer)
    db.session.commit()
    flash('Offer submitted successfully!', 'success')
    return redirect(url_for('recycler.dashboard'))
