import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

with open ('secret_key.txt', 'r') as f:
    key = f.read()

app.secret_key = key

def get_db_connection():
    conn = sqlite3.connect('birthdays.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'] # In a real app, you'd hash this!
        name = request.form['name']
        room_no = request.form.get('room_no', '') # .get() allows it to be optional
        dob = request.form.get('dob', '')

        conn = get_db_connection()
        try:
            conn.execute(
                'INSERT INTO users (username, password, name, room_no, dob) VALUES (?, ?, ?, ?, ?)',
                (username, password, name, room_no, dob)
            )
            
            # If they provided a DOB, let's automatically add them to the birthday tracker too!
            if dob:
                conn.execute('INSERT INTO students (name, dob) VALUES (?, ?)', (name, dob))
                
            conn.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            error = "Username already exists. Choose another one."
        finally:
            conn.close()

    return render_template('register.html', error=error)

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    error = None
    
    ADMIN_USERS = {
        "admin": "admin",
        "Sujan": "Sujan@Sil@2007",
        "Ishaan": "Lol1234cool"
    }
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # 2. Check if they are in the list AND the password matches
        if username in ADMIN_USERS and ADMIN_USERS[username] == password:
            session['is_admin'] = True
            session['logged_in_user'] = username # Logs you in under your specific admin name
            return redirect(url_for('admin_dashboard'))
        else:
            error = "Invalid Admin Credentials"

    return render_template('admin_login.html', error=error)

@app.route('/admin-dashboard')
def admin_dashboard():
    # Security check: Kick them out if they aren't an admin
    if not session.get('is_admin'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    
    # 1. Get all registered users (for Column 2)
    users = conn.execute('SELECT * FROM users').fetchall()
    
    # 2. Get all birthday entries (for Column 1 List)
    all_birthdays = conn.execute('SELECT * FROM students').fetchall()

    # NEW: Fetch all pending birthday requests
    bday_requests = conn.execute('SELECT * FROM birthday_requests').fetchall()

    #Fetch all the suggestions
    suggestions = conn.execute('SELECT * FROM suggestions').fetchall()
    conn.close()



    # 3. Calculate Upcoming Birthday (for Column 1 Spotlight)
    today = datetime.now()
    upcoming_birthdays = []
    
    for student in all_birthdays:
        dob = datetime.strptime(student['dob'], '%Y-%m-%d')
        bday_this_year = datetime(today.year, dob.month, dob.day)
        
        if bday_this_year < today:
            bday_this_year = datetime(today.year + 1, dob.month, dob.day)
            
        days_until = (bday_this_year - today).days
        upcoming_birthdays.append({
            'id': student['id'],
            'name': student['name'],
            'dob': dob.strftime("%B %d"), 
            'days_until': days_until,
            'raw_dob': student['dob'] # Keeping raw date for editing later
        })

    upcoming_birthdays.sort(key=lambda x: x['days_until'])
    next_birthday = upcoming_birthdays[0] if upcoming_birthdays else None

    return render_template('admin_dashboard.html', 
                           users=users, 
                           all_birthdays=upcoming_birthdays,
                           next_birthday=next_birthday,
                            bday_requests = bday_requests,
                            suggestions = suggestions)


@app.route('/delete_birthday/<int:student_id>')
def delete_birthday(student_id):
    if not session.get('is_admin'):
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    conn.execute('DELETE FROM students WHERE id = ?', (student_id,))
    conn.commit()
    conn.close()
    
    return redirect(url_for('admin_dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
        conn.close()

        if user:
            # Login successful! Save their username in the session
            session['logged_in_user'] = user['username']
            session['user_name'] = user['name']
            return redirect(url_for('home'))
        else:
            error = "Invalid username or password."

    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear() # Deletes the session data
    return redirect(url_for('login'))

@app.route('/')
def home():
    # Check if the user is logged in
    if 'logged_in_user' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    students = conn.execute('SELECT * FROM students').fetchall()
    conn.close()

    today = datetime.now()
    current_date_str = today.strftime("%B %d, %Y") # e.g., September 13, 2026

    upcoming_birthdays = []
    next_birthdays = []
    today_birthdays = []
    rest_upcoming = []
    # Logic to calculate upcoming birthdays
    for student in students:
        dob = datetime.strptime(student['dob'], '%Y-%m-%d')
        # Create a birthday date for the current year
        bday_this_year = datetime(today.year, dob.month, dob.day +1)
        
        # If the birthday has already passed this year, look at next year
        if bday_this_year < today:
            bday_this_year = datetime(today.year + 1, dob.month, dob.day)
            
        days_until = (bday_this_year - today).days
        if (days_until == 0) :
            # Birthday is today
            today_birthdays.append({
                'name' : student['name'],
                'dob': dob.strftime("%B %d"), 
                'days_until': days_until
            })
        
        
        upcoming_birthdays.append({
            'name': student['name'],
            'dob': dob.strftime("%B %d"), 
            'days_until': days_until
        })

    # Sort the list so the closest birthdays are at the top
    upcoming_birthdays.sort(key=lambda x: x['days_until'])

    # Split into "Next Birthday" (top box) and "All Upcoming" (bottom box)
    if upcoming_birthdays :
            closest_date = upcoming_birthdays[0]['days_until']

            for person in upcoming_birthdays :
                if person['days_until'] == closest_date:
                    next_birthdays.append(person)
                else :
                    rest_upcoming.append(person)
    # rest_upcoming = upcoming_birthdays[1:] if len(upcoming_birthdays) > 1 else []

    return render_template('index.html',
                           next_birthdays = next_birthdays,
                           today_birthdays = today_birthdays, 
                           current_date=current_date_str, 
                           rest_upcoming=rest_upcoming)

# --- 1. Quick Add Route (For the Dashboard) ---
@app.route('/admin/add_birthday', methods=['POST'])
def admin_add_birthday():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    name = request.form['student_name']
    dob = request.form['student_dob']
    
    conn = get_db_connection()
    conn.execute('INSERT INTO students (name, dob) VALUES (?, ?)', (name, dob))
    conn.commit()
    conn.close()
    
    return redirect(url_for('admin_dashboard'))

# --- 2. Edit Route ---
@app.route('/edit_birthday/<int:student_id>', methods=['GET', 'POST'])
def edit_birthday(student_id):
    if not session.get('is_admin'):
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    
    # If the admin submits the edited form
    if request.method == 'POST':
        name = request.form['student_name']
        dob = request.form['student_dob']
        conn.execute('UPDATE students SET name = ?, dob = ? WHERE id = ?', (name, dob, student_id))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_dashboard'))
        
    # If it's a GET request, fetch the current data to pre-fill the form
    student = conn.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
    conn.close()
    
    return render_template('edit_birthday.html', student=student)

@app.route('/request-birthday', methods=['GET', 'POST'])
def request_birthday():
    if 'logged_in_user' not in session:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        name = request.form['name']
        dob = request.form['dob'] # <--- Capturing the new DOB field
        room_no = request.form.get('room_no', '')
        requested_by = session['logged_in_user'] # <--- Automatically tracking who sent it
        
        proof_filename = ""
        if 'proof' in request.files:
            file = request.files['proof']
            if file.filename != '': 
                proof_filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], proof_filename))
        
        conn = get_db_connection()
        conn.execute('INSERT INTO birthday_requests (name, dob, room_no, proof, requested_by) VALUES (?, ?, ?, ?, ?)', 
                     (name, dob, room_no, proof_filename, requested_by))
        conn.commit()
        conn.close()
        
        return redirect(url_for('home'))
        
    return render_template('request_birthday.html')

@app.route('/admin/approve_request/<int:req_id>')
def approve_request(req_id):
    if not session.get('is_admin'):
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    # 1. Get the request data
    req = conn.execute('SELECT * FROM birthday_requests WHERE id = ?', (req_id,)).fetchone()
    
    if req:
        # 2. Insert it into the official students table
        conn.execute('INSERT INTO students (name, dob) VALUES (?, ?)', (req['name'], req['dob']))
        # 3. Delete it from the pending requests table
        conn.execute('DELETE FROM birthday_requests WHERE id = ?', (req_id,))
        conn.commit()
        
    conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/reject_request/<int:req_id>')
def reject_request(req_id):
    if not session.get('is_admin'):
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    conn.execute('DELETE FROM birthday_requests WHERE id = ?', (req_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/plan', methods = ['GET', 'POST'])
def plan() :
    if 'logged_in_user' not in session:
        return redirect(url_for('login'))

    return render_template('plan.html')

@app.route('/suggestion', methods=['GET', 'POST'])
def suggestion() :
    if 'logged_in_user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST' :
        name = request.form.get('name','')
        suggestion_text = request.form['Suggestion']
        conn = get_db_connection()
        conn.execute('INSERT INTO suggestions (name, suggestion_text) VALUES (?, ?)', 
                         (name, suggestion_text))
        conn.commit()
        conn.close()
        return redirect(url_for('home'))
    return render_template('suggestion.html')

if __name__ == '__main__':
    app.run(debug=True)