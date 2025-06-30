# app.py
from flask import Flask, render_template, request, redirect, url_for, session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['MONGO_URI'] = "mongodb+srv://rajathda:Sp99l0ZXuszijwar@cluster0.x9apgd4.mongodb.net/letzstudy?retryWrites=true&w=majority&tls=true"

load_dotenv()

app.config['MONGO_URI'] = os.getenv("MONGO_URI")

mongo = PyMongo(app)

UPLOAD_FOLDER = 'static/uploads/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Admin login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = mongo.db.admins.find_one({'username': username})
        if admin and check_password_hash(admin['password'], password):
            session['admin'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    month_filter = request.args.get('month')
    if month_filter:
        students = mongo.db.students.find({'month': month_filter})
    else:
        students = mongo.db.students.find()
    return render_template('index.html', students=students)


@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('login'))

# Home - List all students
@app.route('/')
def index():
    if 'admin' not in session:
        return redirect(url_for('login'))
    students = mongo.db.students.find()
    return render_template('index.html', students=students)

# Create new student profile
@app.route('/create', methods=['GET', 'POST'])
def create():
    if 'admin' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        course = request.form['course']
        month = request.form['month']

        
        mongo.db.students.insert_one({
            'name': name,
            'email': email,
            'phone': phone,
            'course': course,
            'month':month,
            'admin_notes': ''
        })
        return redirect(url_for('index'))
    return render_template('create.html')

# View student profile & admin note
@app.route('/student/<id>', methods=['GET', 'POST'])
def student(id):
    if 'admin' not in session:
        return redirect(url_for('login'))

    student = mongo.db.students.find_one({'_id': ObjectId(id)})

    if request.method == 'POST':
        checklist_fields = [
            'passport_size_photo', '10th_markscard', '12th_markscard', 'consolidated_markscard','individual_markscards', 'PDC', 'degree_certificate',
                             'ielts', 'gre', 'gmat', 'passport', 'LOR1', 'LOR2', 'resume', 'SOP', 'bank_statement', 'experience'
        ]

        checklist = {field: field in request.form for field in checklist_fields}

        note_dates = request.form.getlist('note_date[]')
        note_texts = request.form.getlist('note_text[]')
        
        note_entries = [
            {'date': d.strip(), 'text': t.strip()}
            for d, t in zip(note_dates, note_texts)
            if d.strip() or t.strip()
        ]
         
        imp_points = {'imp_notes' :request.form.get('imp_notes')}


        additional_fields = {
            'board_10th': request.form.get('board_10th', ''),
            'percent_10th': request.form.get('percent_10th', ''),
            'board_12th': request.form.get('board_12th', ''),
            'yop_12': request.form.get('yop_12', ''),
            'yop_10': request.form.get('yop_10', ''),
            'yop_UG': request.form.get('yop_UG', ''),
            'GRE': request.form.get('GRE', ''),
            'GRE_dropdown': request.form.get('GRE_dropdown', ''),
            'IELTS': request.form.get('IELTS', ''),
            'IELTS_dropdown': request.form.get('IELTS_dropdown', ''),
            'GMAT': request.form.get('GMAT', ''),
            'GMAT_dropdown': request.form.get('GMAT_dropdown', ''),
            'percent_12th': request.form.get('percent_12th', ''),
            'english_12th': request.form.get('english_12th', ''),
            'cgpa': request.form.get('cgpa', ''),
            'course_name': request.form.get('course_name', ''),
            'degree_name': request.form.get('degree_name', ''),
            'college_name': request.form.get('college_name', ''),
            'paid_amount': request.form.get('paid_amount', ''),
            'due_amount': request.form.get('due_amount', '')
        }

        update_fields = {
            **checklist,
            **additional_fields,
            **imp_points,
            'note_entries': note_entries,
            
        }

        mongo.db.students.update_one(
            {'_id': ObjectId(id)},
            {'$set': update_fields}
        )

        return redirect(url_for('student', id=id))

    return render_template('student.html', student=student)

if __name__ == '__main__':
    #Uncomment below line once to create admin account
    
    mongo.db.admins.update_one(
    {'username': 'admin'},  # Filter: find the document
    {'$set': {'password': generate_password_hash('admin@123')}})
    app.run(debug=True)
