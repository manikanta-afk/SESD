import os, uuid
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import select, func

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-only-change-this-secret')
uri = os.getenv('DATABASE_URL', 'sqlite:///smartpark.db')
if uri.startswith('postgres://'):
    uri = uri.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_pre_ping': True}
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(160), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='customer')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class ParkingLot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(180), nullable=False)
    description = db.Column(db.Text, default='')
    hourly_rate = db.Column(db.Numeric(10, 2), nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)
    slots = db.relationship('ParkingSlot', backref='lot', lazy=True, cascade='all, delete-orphan')

class ParkingSlot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False, index=True)
    slot_number = db.Column(db.String(20), nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)
    __table_args__ = (db.UniqueConstraint('lot_id', 'slot_number', name='uq_parking_slot'),)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    slot_id = db.Column(db.Integer, db.ForeignKey('parking_slot.id'), nullable=False, index=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    vehicle_number = db.Column(db.String(24), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='confirmed')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user = db.relationship('User', backref='bookings')
    slot = db.relationship('ParkingSlot', backref='bookings')


def signed_in(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('login', next=request.path))
        return fn(*args, **kwargs)
    return wrapped

def is_available(slot_id, start, end):
    slot = db.session.get(ParkingSlot, slot_id)
    if not slot or not slot.active or not slot.lot.active:
        return False
    conflict = Booking.query.filter(Booking.slot_id == slot_id, Booking.status == 'confirmed',
        Booking.start_time < end, Booking.end_time > start).first()
    return conflict is None

def parse_window(date_text=None, start_text=None, hours=1):
    day = date_text or datetime.now().strftime('%Y-%m-%d')
    start_text = start_text or datetime.now().strftime('%H:%M')
    start = datetime.strptime(day + ' ' + start_text, '%Y-%m-%d %H:%M')
    return start, start + timedelta(hours=hours)

@app.context_processor
def inject_globals():
    return {'current_user': session.get('name'), 'current_role': session.get('role')}

@app.route('/')
@app.route('/dashboard')
@signed_in
def dashboard():
    lots = ParkingLot.query.filter_by(active=True).order_by(ParkingLot.id).all()
    selected_id = request.args.get('lot', type=int)
    selected = next((x for x in lots if x.id == selected_id), lots[0] if lots else None)
    start = datetime.now().replace(second=0, microsecond=0) + timedelta(minutes=5)
    bookings = Booking.query.filter_by(user_id=session['user_id']).order_by(Booking.created_at.desc()).limit(6).all()
    active_count = Booking.query.filter_by(user_id=session['user_id'], status='confirmed').filter(Booking.end_time > datetime.now()).count()
    all_confirmed = Booking.query.filter_by(user_id=session['user_id'], status='confirmed').all()
    total_hours = sum((b.end_time - b.start_time).total_seconds() / 3600 for b in all_confirmed)
    total_saved = sum(float(b.amount) for b in all_confirmed)
    return render_template('dashboard.html', lots=lots, selected=selected, start=start, bookings=bookings,
        active_count=active_count, total_hours=round(float(total_hours),1), total_saved=round(total_saved,2))

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name=request.form.get('name','').strip(); email=request.form.get('email','').strip().lower(); password=request.form.get('password','')
        if not name or '@' not in email or len(password)<8:
            flash('Enter your name, valid email and a password with at least 8 characters.', 'error')
        elif User.query.filter_by(email=email).first():
            flash('An account with this email already exists.', 'error')
        else:
            user=User(name=name,email=email,password_hash=generate_password_hash(password))
            db.session.add(user); db.session.commit(); flash('Account created. Please sign in.', 'success'); return redirect(url_for('login'))
    return render_template('auth.html', mode='register')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user=User.query.filter_by(email=request.form.get('email','').strip().lower()).first()
        if user and check_password_hash(user.password_hash,request.form.get('password','')):
            session.clear(); session['user_id']=user.id; session['name']=user.name; session['role']=user.role
            return redirect(url_for('dashboard'))
        flash('Incorrect email or password.', 'error')
    return render_template('auth.html', mode='login')

@app.route('/logout')
def logout():
    session.clear(); return redirect(url_for('login'))

@app.route('/api/availability/<int:lot_id>')
@signed_in
def availability(lot_id):
    lot=db.get_or_404(ParkingLot,lot_id)
    try:
        start,end=parse_window(request.args.get('date'),request.args.get('start'),int(request.args.get('hours',1)))
    except (ValueError, TypeError):
        return jsonify({'error':'Invalid date, start time or duration'}),400
    data=[]
    for slot in lot.slots:
        if slot.active:
            data.append({'id':slot.id,'number':slot.slot_number,'available':is_available(slot.id,start,end)})
    return jsonify({'slots':data,'server_time':datetime.now().isoformat(timespec='seconds')})

@app.route('/api/bookings', methods=['POST'])
@signed_in
def create_booking():
    payload=request.get_json(silent=True) or {}
    try:
        slot_id=int(payload.get('slot_id')); hours=int(payload.get('hours',1))
        if hours not in (1,2,3,4,5,6,7,8): raise ValueError()
        start,end=parse_window(payload.get('date'),payload.get('start'),hours)
    except (ValueError,TypeError):
        return jsonify({'ok':False,'message':'Choose a valid booking time and duration.'}),400
    vehicle=(payload.get('vehicle_number') or '').strip().upper()
    if not vehicle or len(vehicle)>24:
        return jsonify({'ok':False,'message':'Enter a valid vehicle registration number.'}),400
    if start <= datetime.now():
        return jsonify({'ok':False,'message':'Select a future start time.'}),400
    try:
        # Lock the slot row on databases that support SELECT FOR UPDATE (e.g. PostgreSQL).
        slot=db.session.execute(select(ParkingSlot).where(ParkingSlot.id==slot_id).with_for_update()).scalar_one_or_none()
        if not slot or not slot.active or not slot.lot.active:
            db.session.rollback(); return jsonify({'ok':False,'message':'This parking slot is not active.'}),404
        if not is_available(slot_id,start,end):
            db.session.rollback(); return jsonify({'ok':False,'message':'This slot was just reserved by another customer. Choose another slot.'}),409
        amount=round(float(slot.lot.hourly_rate)*hours,2)
        booking=Booking(code='SP'+uuid.uuid4().hex[:9].upper(),user_id=session['user_id'],slot_id=slot_id,
            start_time=start,end_time=end,vehicle_number=vehicle,amount=amount,status='confirmed')
        db.session.add(booking); db.session.commit()
        return jsonify({'ok':True,'booking':{'code':booking.code,'slot':slot.slot_number,'lot':slot.lot.name,
            'vehicle':vehicle,'hours':hours,'amount':amount,'start':start.strftime('%d %b %Y, %I:%M %p')}})
    except Exception:
        db.session.rollback(); app.logger.exception('Booking failed')
        return jsonify({'ok':False,'message':'Booking could not be saved. Please try again.'}),500

@app.route('/api/my-bookings')
@signed_in
def my_bookings():
    items=Booking.query.filter_by(user_id=session['user_id']).order_by(Booking.created_at.desc()).limit(10).all()
    return jsonify([{'code':b.code,'slot':b.slot.slot_number,'lot':b.slot.lot.name,'amount':float(b.amount),'status':b.status,
        'created':b.created_at.strftime('%d %b %Y')} for b in items])

@app.route('/my-bookings')
@signed_in
def my_bookings():
    bookings=Booking.query.filter_by(user_id=session['user_id']).order_by(Booking.created_at.desc()).all()
    return render_template('my_bookings.html', bookings=bookings)

@app.route('/booking/<code>')
@signed_in
def booking_receipt(code):
    booking=Booking.query.filter_by(code=code).first_or_404()
    if booking.user_id != session['user_id'] and session.get('role')!='admin':
        return 'Forbidden',403
    return render_template('receipt.html',booking=booking)

@app.route('/admin')
@signed_in
def admin():
    if session.get('role')!='admin': return redirect(url_for('dashboard'))
    users=User.query.filter_by(role='customer').count()
    bookings=Booking.query.order_by(Booking.created_at.desc()).limit(30).all()
    return render_template('admin.html',users=users,bookings=bookings,lots=ParkingLot.query.all())

@app.cli.command('init-db')
def init_db():
    db.create_all()
    if not User.query.filter_by(email='admin@smartpark.local').first():
        db.session.add(User(name='SmartPark Admin',email='admin@smartpark.local',
            password_hash=generate_password_hash(os.getenv('ADMIN_PASSWORD','Admin@12345')),role='admin'))
    if ParkingLot.query.count()==0:
        seeds=[('SR University — Main Gate','Warangal',30,'A'),('Central Market Parking','Hanamkonda',25,'B'),('City Centre Parking','Warangal',40,'C')]
        for name,location,rate,prefix in seeds:
            lot=ParkingLot(name=name,location=location,hourly_rate=rate,description='Secure, convenient parking with live reservation status.')
            db.session.add(lot); db.session.flush()
            for n in range(1,21): db.session.add(ParkingSlot(lot_id=lot.id,slot_number=f'{prefix}{n:02d}'))
    db.session.commit()
    print('SmartPark database initialized.')

with app.app_context():
    db.create_all()

if __name__=='__main__':
    app.run(host='0.0.0.0',port=int(os.getenv('PORT',5000)),debug=os.getenv('FLASK_DEBUG')=='1')
