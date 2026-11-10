import os
os.environ['DATABASE_URL']='sqlite://'
os.environ['SECRET_KEY']='test-secret'
from app import app, db, User, ParkingLot, ParkingSlot
from werkzeug.security import generate_password_hash

def test_register_login_dashboard_and_live_api():
    app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    with app.app_context():
        db.drop_all(); db.create_all()
        lot=ParkingLot(name='Test lot',location='Test city',hourly_rate=20)
        db.session.add(lot); db.session.flush()
        db.session.add(ParkingSlot(lot_id=lot.id,slot_number='T01')); db.session.commit()
    client=app.test_client()
    response=client.post('/register',data={'name':'Test Customer','email':'test@example.com','password':'password123'},follow_redirects=True)
    assert response.status_code==200
    response=client.post('/login',data={'email':'test@example.com','password':'password123'},follow_redirects=True)
    assert response.status_code==200
    response=client.get('/api/availability/1?date=2099-01-01&start=10:00&hours=1')
    assert response.status_code==200
    assert response.get_json()['slots'][0]['available'] is True
