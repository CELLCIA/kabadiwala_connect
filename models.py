from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20), nullable=False) # 'collector', 'recycler', 'admin'
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # Collector/Recycler common
    name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    location = db.Column(db.String(200))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    # Recycler specific
    auth_number = db.Column(db.String(100))
    materials_accepted = db.Column(db.String(500))
    is_verified = db.Column(db.Boolean, default=False)
    pickup_available = db.Column(db.Boolean, default=False)
    
    # Collector specific
    preferred_language = db.Column(db.String(10), default='en')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Material(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100))
    description = db.Column(db.String(255))
    icon = db.Column(db.String(50))

class Price(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    material_id = db.Column(db.Integer, db.ForeignKey('material.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), default='kg')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    material = db.relationship('Material', backref=db.backref('prices', lazy=True))

class Lot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    collector_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('material.id'), nullable=False)
    weight = db.Column(db.Float, nullable=False)
    condition = db.Column(db.String(50))
    photo_filename = db.Column(db.String(255))
    estimated_value = db.Column(db.Float)
    status = db.Column(db.String(20), default='DRAFT') # DRAFT, SUBMITTED, OFFER_RECEIVED, ACCEPTED, COMPLETED, CANCELLED
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    collector = db.relationship('User', foreign_keys=[collector_id], backref=db.backref('lots', lazy=True))
    material = db.relationship('Material')

class Offer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('lot.id'), nullable=False)
    recycler_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    price_per_kg = db.Column(db.Float, nullable=False)
    pickup_available = db.Column(db.Boolean, default=False)
    pickup_date = db.Column(db.DateTime)
    message = db.Column(db.String(255))
    status = db.Column(db.String(20), default='PENDING') # PENDING, ACCEPTED, REJECTED
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    lot = db.relationship('Lot', backref=db.backref('offers', lazy=True))
    recycler = db.relationship('User', foreign_keys=[recycler_id])

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('lot.id'), nullable=False)
    recycler_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    final_price = db.Column(db.Float)
    payment_status = db.Column(db.String(20), default='PENDING') # PENDING, PAID
    status = db.Column(db.String(20), default='ACCEPTED') # ACCEPTED, PICKUP_REQUESTED, HANDED_OVER, RECYCLING, COMPLETED
    handover_id = db.Column(db.String(50), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    lot = db.relationship('Lot', backref=db.backref('transaction', uselist=False))
    recycler = db.relationship('User', foreign_keys=[recycler_id])

class Traceability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=False)
    event = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    actor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    transaction = db.relationship('Transaction', backref=db.backref('traceability', lazy=True, order_by='Traceability.timestamp'))
    actor = db.relationship('User', foreign_keys=[actor_id])
