from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = 'your_secret_key'
CORS(app)

def get_db_connection():
    conn = sqlite3.connect('company.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['id']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM Administration WHERE id = ?', (user_id,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            if user['role'] == 'HR':
                return redirect(url_for('hr_dashboard'))
            else:
                return redirect(url_for('employee_dashboard'))
        else:
            return 'Invalid credentials'
    return render_template('login.html')

@app.route('/hr_dashboard')
def hr_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    employees = conn.execute('SELECT * FROM Employees').fetchall()
    conn.close()
    return render_template('hr.html', employees=employees)

@app.route('/employee_dashboard')
def employee_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    employee = conn.execute('SELECT * FROM Employees WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return render_template('employee.html', employee=employee)

@app.route('/add_employee', methods=['POST'])
def add_employee():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        user_id = request.form['id']
        password = generate_password_hash(request.form['password'])
        role = request.form.get('role', 'employee')

        conn = get_db_connection()
        conn.execute('INSERT INTO Administration (id, password, role) VALUES (?, ?, ?)', (user_id, password, role))
        conn.commit()
        conn.close()

        return redirect(url_for('hr_dashboard'))
    return render_template('add_employee.html')

@app.route('/update_employee', methods=['POST'])
def update_employee():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    employee_id = request.form['id']
    name = request.form['name']
    marital_status = request.form['marital_status']
    position = request.form['position']
    educational_background = request.form['educational_background']
    employment_status = request.form['employment_status']
    onboarding_time = request.form['onboarding_time']

    conn = get_db_connection()
    conn.execute('''
        INSERT INTO Employees (id, name, marital_status, position, educational_background, employment_status, onboarding_time)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
        name=excluded.name,
        marital_status=excluded.marital_status,
        position=excluded.position,
        educational_background=excluded.educational_background,
        employment_status=excluded.employment_status,
        onboarding_time=excluded.onboarding_time
    ''', (employee_id, name, marital_status, position, educational_background, employment_status, onboarding_time))
    conn.commit()
    conn.close()

    return redirect(url_for('hr_dashboard'))

@app.route('/delete_employee', methods=['POST'])
def delete_employee():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    employee_id = request.form['id']

    conn = get_db_connection()
    conn.execute('DELETE FROM Administration WHERE id = ?', (employee_id,))
    conn.execute('DELETE FROM Employees WHERE id = ?', (employee_id,))
    conn.execute('DELETE FROM Salary WHERE id = ?', (employee_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('hr_dashboard'))

@app.route('/update_salary', methods=['POST'])
def update_salary():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    salary_id = request.form['id']
    name = request.form['name']
    basic_salary = float(request.form['basic_salary'])
    performance_bonus = float(request.form['performance_bonus'])
    overtime_pay = float(request.form['overtime_pay'])
    allowances = float(request.form['allowances'])
    deductions = float(request.form['deductions'])
    salary = basic_salary + performance_bonus + overtime_pay + allowances - deductions
    date = request.form['date']

    conn = get_db_connection()
    conn.execute('''
        INSERT INTO Salary (id, name, basic_salary, performance_bonus, overtime_pay, allowances, deductions, salary, date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            name=excluded.name,
            basic_salary=excluded.basic_salary,
            performance_bonus=excluded.performance_bonus,
            overtime_pay=excluded.overtime_pay,
            allowances=excluded.allowances,
            deductions=excluded.deductions,
            salary=excluded.salary,
            date=excluded.date
    ''', (salary_id, name, basic_salary, performance_bonus, overtime_pay, allowances, deductions, salary, date))
    conn.commit()
    conn.close()

    return redirect(url_for('hr_dashboard'))

@app.route('/salary_dashboard')
def salary_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    salary_records = conn.execute('SELECT * FROM Salary').fetchall()
    conn.close()
    return render_template('salary.html', salary_records=salary_records)

@app.route('/change_password', methods=['POST'])
def change_password():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    current_password = request.form['current_password']
    new_password = request.form['new_password']
    confirm_new_password = request.form['confirm_new_password']
    user_id = session['user_id']

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM Administration WHERE id = ?', (user_id,)).fetchone()

    if user and check_password_hash(user['password'], current_password):
        if new_password == confirm_new_password:
            new_password_hash = generate_password_hash(new_password)
            conn.execute('UPDATE Administration SET password = ? WHERE id = ?', (new_password_hash, user_id))
            conn.commit()
            conn.close()
            return 'Password changed successfully'
        else:
            conn.close()
            return 'New passwords do not match'
    else:
        conn.close()
        return 'Incorrect current password'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1833, debug=True)