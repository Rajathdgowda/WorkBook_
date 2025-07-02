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
        month = request.form['month']

        
        mongo.db.students.insert_one({
            'name': name,
            'email': email,
            'phone': phone,
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
            '10th_Markscard', '12th_Markscard', 'Individual_Markscards', 'Consolidated_Markscard', 'PDC',
            'Degree_Certificate', 'Passport', 'Resume', 'LOR1', 'LOR2', 'SOP', 'Passport_size_photo',
            'Bank_Statement', 'Experience', 'IELTS', 'GRE', 'GMAT'
        ]
        checklist = {field: field in request.form for field in checklist_fields}

        # Notes (Calendar)
        note_dates = request.form.getlist('note_date[]')
        note_texts = request.form.getlist('note_text[]')
        note_entries = [
            {'date': d.strip(), 'text': t.strip()}
            for d, t in zip(note_dates, note_texts)
            if d.strip() or t.strip()
        ]

        # Important Notes
        imp_points = {'imp_notes': request.form.get('imp_notes', '')}

        # University Fields (from hidden inputs)
        university_fields = {
            'university_name': request.form.get('university_name', '') or student.get('university_name', ''),
            'university_country': request.form.get('university_country', '') or student.get('university_country', ''),
            'university_groups': request.form.get('university_groups', '')or student.get('university_groups', '')
        }
        
        


        # Academic + Fee Fields
        additional_fields = {
            'board_10th': request.form.get('board_10th', ''),
            'percent_10th': request.form.get('percent_10th', ''),
            'board_12th': request.form.get('board_12th', ''),
            'percent_12th': request.form.get('percent_12th', ''),
            'yop_10': request.form.get('yop_10', ''),
            'yop_12': request.form.get('yop_12', ''),
            'yop_UG': request.form.get('yop_UG', ''),
            'english_12th': request.form.get('english_12th', ''),
            'cgpa': request.form.get('cgpa', ''),
            'course_name': request.form.get('course_name', ''),
            'degree_name': request.form.get('degree_name', ''),
            'college_name': request.form.get('college_name', ''),
            'GRE_marks': request.form.get('GRE_marks', ''),
            'GRE_dropdown': request.form.get('GRE_dropdown', ''),
            'IELTS_marks': request.form.get('IELTS_marks', ''),
            'IELTS_dropdown': request.form.get('IELTS_dropdown', ''),
            'GMAT_marks': request.form.get('GMAT_marks', ''),
            'GMAT_dropdown': request.form.get('GMAT_dropdown', ''),
            'paid_amount': request.form.get('paid_amount', ''),
            'due_amount': request.form.get('due_amount', '')
        }

        # Final Mongo update
        update_fields = {
            **checklist,
            **additional_fields,
            **imp_points,
            **university_fields,
            'note_entries': note_entries
        }

        mongo.db.students.update_one(
            {'_id': ObjectId(id)},
            {'$set': update_fields}
        )

        return redirect(url_for('student', id=id))

    return render_template('student.html', student=student)

from flask import Flask, render_template, request, jsonify
# import pandas as pd

# # Load all Excel files
# def load_universities():
#     sources = {
#         'Kings': 'kings.xlsx',
#         # 'Superior': 'superior.xlsx',
#         # 'Global': 'global.xlsx'
#     }
#     data = {}

#     for group, file in sources.items():
#         df = pd.read_excel(file)
#         for _, row in df.iterrows():
#             name = str(row['University/Institution Name']).strip()
#             key = name.lower()
#             country = str(row.get('State', 'Unknown')).strip()

#             if key not in data:
#                 data[key] = {'name': name, 'groups': set(), 'country': country}
#             data[key]['groups'].add(group)
#     return data

# university_data = load_universities()

# @app.route('/search')
# def search():
#     term = request.args.get('term', '').lower()
#     results = []

#     if term:
#         for key, info in university_data.items():
#             if term in key:
#                 results.append({
#                     'name': info['name'],
#                     'country': info['country'],
#                     'groups': list(info['groups'])
#                 })

#     return jsonify(results[:10])  # limit to 10 results


import os
import pandas as pd

def load_universities():
    sources = {
        'Kings': 'kings.xlsx',
        'Superior': 'superior.xlsx',
        'Global': 'global.xlsx',
        
    }

    data = {}

    for group, file in sources.items():
        if not os.path.exists(file):
            continue

        # Load all sheets; sheet_name=None returns a dict of DataFrames
        sheets = pd.read_excel(file, sheet_name=None)

        for sheet_name, df in sheets.items():
            country = sheet_name.strip()  # Use sheet name as country

            for _, row in df.iterrows():
                name = str(row.get('University/Institution Name', '')).strip()
                if not name:
                    continue

                key = name.lower()

                if key not in data:
                    data[key] = {
                        'name': name,
                        'groups': set(),
                        'country': country
                    }

                data[key]['groups'].add(group)

    return data

university_data = load_universities()

@app.route('/search')
def search():
    term = request.args.get('term', '').lower()
    results = []

    if term:
        for key, info in university_data.items():
            if term in key:
                results.append({
                    'name': info['name'],
                    'country': info['country'],
                    'groups': list(info['groups'])
                })

    return jsonify(results[:10])

if __name__ == '__main__':
    #Uncomment below line once to create admin account
    
    mongo.db.admins.update_one(
    {'username': 'admin'},  # Filter: find the document
    {'$set': {'password': generate_password_hash('admin@123')}})
    app.run(debug=True)
