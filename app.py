from flask import Flask, render_template, request, redirect, url_for, session, jsonify
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


@app.route('/fetch_salary')
def fetch_salary():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    salary_data = conn.execute('SELECT * FROM Salary WHERE employee_id = ?', (user_id,)).fetchone()
    conn.close()

    if salary_data:
        salary_info = {
            'basic_salary': salary_data['basic_salary'],
            'performance_bonus': salary_data['performance_bonus'],
            'overtime_pay': salary_data['overtime_pay'],
            'allowances': salary_data['allowances'],
            'deductions': salary_data['deductions'],
            'salary': salary_data['salary'],
            'date': salary_data['date']
        }
    else:
        salary_info = {
            'basic_salary': 0.0,
            'performance_bonus': 0.0,
            'overtime_pay': 0.0,
            'allowances': 0.0,
            'deductions': 0.0,
            'salary': 0.0,
            'date': 'N/A'
        }

    return jsonify(salary_info)


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
    conn.execute('DELETE FROM Salary WHERE employee_id = ?', (employee_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('hr_dashboard'))


@app.route('/update_salary', methods=['POST'])
def update_salary():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    id = request.form['id']
    name = request.form['name']
    basic_salary = float(request.form['basic_salary'])
    performance_bonus = float(request.form['performance_bonus'])
    overtime_pay = float(request.form['overtime_pay'])
    allowances = float(request.form['allowances'])
    deductions = float(request.form['deductions'])
    salary = basic_salary + performance_bonus + overtime_pay + allowances - deductions
    date = request.form['date']

    conn = get_db_connection()
    existing_record = conn.execute('SELECT * FROM Salary WHERE employee_id = ? AND date = ?', (id, date)).fetchone()

    if existing_record:
        conn.execute('''
            UPDATE Salary SET
                name = ?,
                basic_salary = ?,
                performance_bonus = ?,
                overtime_pay = ?,
                allowances = ?,
                deductions = ?,
                salary = ?
            WHERE employee_id = ? AND date = ?
        ''', (name, basic_salary, performance_bonus, overtime_pay, allowances, deductions, salary, id, date))
    else:
        conn.execute('''
            INSERT INTO Salary (employee_id, name, basic_salary, performance_bonus, overtime_pay, allowances, deductions, salary, date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (id, name, basic_salary, performance_bonus, overtime_pay, allowances, deductions, salary, date))

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

    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_new_password = request.form.get('confirm_new_password')
    user_id = session['user_id']

    if not current_password or not new_password or not confirm_new_password:
        return jsonify({'success': False, 'msg': 'Missing fields in form submission'}), 4100

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM Administration WHERE id = ?', (user_id,)).fetchone()

    if user and check_password_hash(user['password'], current_password):
        if new_password == confirm_new_password:
            new_password_hash = generate_password_hash(new_password)
            conn.execute('UPDATE Administration SET password = ? WHERE id = ?', (new_password_hash, user_id))
            conn.commit()
            conn.close()
            return jsonify({'success': True, 'msg': 'Password changed successfully'})
        else:
            conn.close()
            return jsonify({'success': False, 'msg': 'New passwords do not match'}), 4200
    else:
        conn.close()
        return jsonify({'success': False, 'msg': 'Incorrect current password'}), 4300


@app.route('/employee_salary', methods=['GET'])
def employee_salary():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    employee_id = request.args.get('employee_id')
    conn = get_db_connection()
    salary_records = conn.execute('SELECT * FROM Salary WHERE employee_id = ?', (employee_id,)).fetchall()
    conn.close()

    salary_list = []
    for record in salary_records:
        salary_list.append({
            'id': record['employee_id'],
            'name': record['name'],
            'basic_salary': record['basic_salary'],
            'performance_bonus': record['performance_bonus'],
            'overtime_pay': record['overtime_pay'],
            'allowances': record['allowances'],
            'deductions': record['deductions'],
            'salary': record['salary'],
            'date': record['date']
        })

    # return jsonify({'success': True, 'employees': salary_list})
    return render_template('salary.html', salary_list=salary_list)


@app.route('/salary/<int:employee_id>')
def salary(employee_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    salary_records = conn.execute('SELECT * FROM Salary WHERE employee_id = ?', (employee_id,)).fetchall()
    conn.close()

    if not salary_records:
        return 'No salary records found for this employee', 404

    salary_list = []
    for record in salary_records:
        salary_list.append({
            'id': record['employee_id'],
            'name': record['name'],
            'basic_salary': record['basic_salary'],
            'performance_bonus': record['performance_bonus'],
            'overtime_pay': record['overtime_pay'],
            'allowances': record['allowances'],
            'deductions': record['deductions'],
            'salary': record['salary'],
            'date': record['date']
        })

    return render_template('salary.html', salary_list=salary_list)


@app.route('/filter_employees', methods=['GET', 'POST'])
def filter_employees():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Retrieve the search filters from the form
        position = request.form.get('position')
        educational_background = request.form.get('educational_background')
        employment_status = request.form.get('employment_status')

        # Build the SQL query with the provided filters
        query = 'SELECT * FROM Employees WHERE 1=1'
        params = []
        if position and position != 'ALL':
            query += ' AND position LIKE ?'
            params.append(f'%{position}%')
        if educational_background and educational_background != 'ALL':
            query += ' AND educational_background LIKE ?'
            params.append(f'%{educational_background}%')
        if employment_status and employment_status != 'ALL':
            query += ' AND employment_status LIKE ?'
            params.append(f'%{employment_status}%')

        conn = get_db_connection()
        employees = conn.execute(query, params).fetchall()
        conn.close()

        # Convert the SQLite row objects to dictionaries
        employees_dict = [dict(row) for row in employees]

        # Prepare the response data
        response_data = {
            'total': len(employees_dict),
            'employees': employees_dict
        }

        # Return the response as JSON
        return jsonify(response_data)

    return redirect(url_for('hr_dashboard'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1833, debug=True)
