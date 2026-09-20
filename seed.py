from app import create_app
from models import db, User, Material, Price
from datetime import datetime

app = create_app()

def seed_data():
    with app.app_context():
        db.create_all()

        # Seed Users
        if not User.query.filter_by(email='admin@example.com').first():
            admin = User(role='admin', email='admin@example.com', name='System Admin')
            admin.set_password('Admin@123')
            db.session.add(admin)

        if not User.query.filter_by(email='collector@example.com').first():
            collector = User(
                role='collector', 
                email='collector@example.com', 
                name='Demo Collector',
                phone='9876543210',
                location='Chennai South',
                latitude=12.97, longitude=80.22,
                preferred_language='en'
            )
            collector.set_password('Collector@123')
            db.session.add(collector)

        if not User.query.filter_by(email='recycler@example.com').first():
            recycler = User(
                role='recycler',
                email='recycler@example.com',
                name='Green Earth Recycling',
                phone='9998887776',
                location='Chennai North',
                latitude=13.10, longitude=80.25,
                auth_number='AUTH-1234-PCB',
                materials_accepted='PCB,Copper,Batteries',
                is_verified=True,
                pickup_available=True
            )
            recycler.set_password('Recycler@123')
            db.session.add(recycler)

        # Seed Materials
        materials_data = [
            {'name': 'Printed Circuit Boards (PCB)', 'category': 'E-Waste', 'icon': 'cpu'},
            {'name': 'Copper Cables', 'category': 'Metals', 'icon': 'lightning'},
            {'name': 'Lithium-ion Batteries', 'category': 'Batteries', 'icon': 'battery-charging'},
            {'name': 'LCD/LED Panels', 'category': 'Displays', 'icon': 'display'},
            {'name': 'Mixed Plastics', 'category': 'Plastics', 'icon': 'recycle'}
        ]
        
        for m_data in materials_data:
            if not Material.query.filter_by(name=m_data['name']).first():
                mat = Material(name=m_data['name'], category=m_data['category'], icon=m_data['icon'])
                db.session.add(mat)
                db.session.commit() # commit to get ID
                
                # Seed Price for this material
                base_price = 100.0 if 'PCB' in mat.name else (300.0 if 'Copper' in mat.name else 50.0)
                price = Price(material_id=mat.id, price=base_price, unit='kg')
                db.session.add(price)

        db.session.commit()
        print("Database seeded successfully.")

if __name__ == '__main__':
    seed_data()
