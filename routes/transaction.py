from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Lot, Offer, Transaction, Traceability
import uuid

transaction_bp = Blueprint('transaction', __name__)

@transaction_bp.route('/lot/<int:lot_id>/offers')
@login_required
def view_offers(lot_id):
    if current_user.role != 'collector':
        return redirect(url_for('main.index'))
    lot = Lot.query.get_or_404(lot_id)
    if lot.collector_id != current_user.id:
        return redirect(url_for('main.index'))
    
    offers = Offer.query.filter_by(lot_id=lot_id, status='PENDING').all()
    return render_template('transaction/view_offers.html', lot=lot, offers=offers)

@transaction_bp.route('/offer/<int:offer_id>/accept', methods=['POST'])
@login_required
def accept_offer(offer_id):
    if current_user.role != 'collector':
        return redirect(url_for('main.index'))
        
    offer = Offer.query.get_or_404(offer_id)
    lot = offer.lot
    if lot.collector_id != current_user.id:
        return redirect(url_for('main.index'))
        
    # Accept offer
    offer.status = 'ACCEPTED'
    lot.status = 'ACCEPTED'
    
    # Reject other offers
    other_offers = Offer.query.filter(Offer.lot_id == lot.id, Offer.id != offer.id).all()
    for o in other_offers:
        o.status = 'REJECTED'
        
    # Create transaction
    handover_id = str(uuid.uuid4())[:8].upper()
    transaction = Transaction(
        lot_id=lot.id,
        recycler_id=offer.recycler_id,
        final_price=offer.price_per_kg * lot.weight,
        handover_id=handover_id
    )
    db.session.add(transaction)
    db.session.flush() # get transaction id
    
    # Add traceability
    trace1 = Traceability(transaction_id=transaction.id, event='LOT CREATED', actor_id=lot.collector_id, timestamp=lot.created_at)
    trace2 = Traceability(transaction_id=transaction.id, event='OFFER ACCEPTED', actor_id=current_user.id)
    db.session.add_all([trace1, trace2])
    
    db.session.commit()
    flash('Offer accepted! Transaction initiated.', 'success')
    return redirect(url_for('transaction.view_handover', tx_id=transaction.id))

@transaction_bp.route('/handover/<int:tx_id>')
@login_required
def view_handover(tx_id):
    transaction = Transaction.query.get_or_404(tx_id)
    # Both collector and recycler can view
    if current_user.id not in [transaction.lot.collector_id, transaction.recycler_id] and current_user.role != 'admin':
        return redirect(url_for('main.index'))
        
    return render_template('transaction/handover.html', tx=transaction)

@transaction_bp.route('/handover/<int:tx_id>/update', methods=['POST'])
@login_required
def update_status(tx_id):
    if current_user.role != 'recycler':
        return redirect(url_for('main.index'))
        
    transaction = Transaction.query.get_or_404(tx_id)
    new_status = request.form.get('status')
    
    valid_statuses = [
        'PICKUP_REQUESTED', 'PICKED UP', 'HANDED OVER', 'RECEIVED', 
        'RECYCLING', 'RECYCLED', 'PAYMENT PENDING', 'PAID', 'COMPLETED'
    ]
    
    if new_status in valid_statuses:
        transaction.status = new_status
        transaction.lot.status = new_status
        
        # Add trace
        trace = Traceability(transaction_id=transaction.id, event=f'STATUS UPDATED TO {new_status}', actor_id=current_user.id)
        db.session.add(trace)
        
        # If Paid, update payment status
        if new_status in ['PAID', 'COMPLETED']:
            transaction.payment_status = 'PAID'
            
        db.session.commit()
        flash(f'Status updated to {new_status}', 'success')
        
    return redirect(url_for('recycler.dashboard'))
