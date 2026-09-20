from flask import Blueprint, render_template
from models import Transaction

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/verify/<handover_id>')
def verify(handover_id):
    transaction = Transaction.query.filter_by(handover_id=handover_id).first_or_404()
    return render_template('verify.html', tx=transaction)
