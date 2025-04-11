from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from reportlab.pdfgen import canvas
from io import BytesIO
import datetime

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'ivf_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ivf.db'
db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    mood_logs = db.relationship('MoodLog', backref='user', lazy=True)
    cycles = db.relationship('CycleLog', backref='user', lazy=True)

class MoodLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mood = db.Column(db.String(100))
    stress = db.Column(db.Integer)
    date = db.Column(db.Date, default=datetime.date.today)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class CycleLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
class CalendarEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    date = db.Column(db.Date)
    time = db.Column(db.String(20))
    notes = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))



# Create tables
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        if User.query.filter_by(username=username).first():
            flash("Username already exists.")
            return redirect('/register')
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            session['user_id'] = user.id
            return redirect('/dashboard')
        flash("Invalid login.")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    user = User.query.get(session['user_id'])
    moods = MoodLog.query.filter_by(user_id=user.id).all()
    cycles = CycleLog.query.filter_by(user_id=user.id).all()
    return render_template('dashboard.html', user=user, moods=moods, cycles=cycles)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    prediction = None
    if request.method == 'POST':
        age = int(request.form['age'])
        bmi = float(request.form['bmi'])
        if age < 30 and bmi < 25:
            prediction = "High"
        elif age < 35:
            prediction = "Moderate"
        else:
            prediction = "Low"
    return render_template('prediction.html', prediction=prediction)

@app.route('/mood', methods=['POST'])
def mood():
    if 'user_id' not in session:
        return redirect('/login')
    mood = request.form['mood']
    stress = int(request.form['stress'])
    entry = MoodLog(mood=mood, stress=stress, user_id=session['user_id'])
    db.session.add(entry)
    db.session.commit()
    return redirect('/dashboard')

@app.route('/cycle', methods=['POST'])
def cycle():
    if 'user_id' not in session:
        return redirect('/login')
    date = datetime.datetime.strptime(request.form['start_date'], "%Y-%m-%d").date()
    notes = request.form['notes']
    entry = CycleLog(start_date=date, notes=notes, user_id=session['user_id'])
    db.session.add(entry)
    db.session.commit()
    return redirect('/dashboard')

@app.route('/export')
def export():
    if 'user_id' not in session:
        return redirect('/login')
    user = User.query.get(session['user_id'])
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.drawString(100, 800, f"IVF Companion Report for {user.username}")
    y = 780
    for mood in user.mood_logs:
        p.drawString(100, y, f"{mood.date}: Mood={mood.mood}, Stress={mood.stress}")
        y -= 20
    for cycle in user.cycles:
        p.drawString(100, y, f"{cycle.start_date}: Notes={cycle.notes}")
        y -= 20
    p.showPage()
    p.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name='ivf_report.pdf', mimetype='application/pdf')

@app.route('/calendar', methods=['GET', 'POST'])
def calendar():
    if 'user_id' not in session:
        return redirect('/login')
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        title = request.form['title']
        date = datetime.datetime.strptime(request.form['date'], "%Y-%m-%d").date()
        time = request.form['time']
        notes = request.form['notes']
        event = CalendarEvent(title=title, date=date, time=time, notes=notes, user_id=user.id)
        db.session.add(event)
        db.session.commit()
        return redirect('/calendar')
    events = CalendarEvent.query.filter_by(user_id=user.id).all()
    return render_template('calendar.html', events=events)

calendar_events = db.relationship('CalendarEvent', backref='user', lazy=True)
# Run the app
if __name__ == '__main__':
    app.run(debug=True)