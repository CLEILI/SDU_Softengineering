import sqlite3
from werkzeug.security import generate_password_hash

# 连接到数据库或创建数据库
conn = sqlite3.connect('company.db')
cursor = conn.cursor()

# 创建 Administration 表
cursor.execute('''
CREATE TABLE IF NOT EXISTS Administration (
    id INTEGER PRIMARY KEY,
    password TEXT,
    role TEXT DEFAULT 'employee'
)
''')

# 创建 Employees 表
cursor.execute('''
CREATE TABLE IF NOT EXISTS Employees (
    id INTEGER PRIMARY KEY,
    name TEXT,
    marital_status TEXT,
    position TEXT,
    educational_background TEXT,
    employment_status TEXT DEFAULT '在职',
    onboarding_time TEXT
)
''')

# 创建 Salary 表，使用employee_id作为外键，id作为主键
cursor.execute('''
CREATE TABLE IF NOT EXISTS Salary (
    id INTEGER PRIMARY KEY,
    employee_id INTEGER,
    name TEXT,
    basic_salary REAL,
    performance_bonus REAL,
    overtime_pay REAL,
    allowances REAL,
    deductions REAL,
    salary REAL,
    date TEXT,
    FOREIGN KEY (employee_id) REFERENCES Employees(id)
)
''')

# 插入一个 ID 为 0，密码为 000 的 HR
hashed_password = generate_password_hash('000')
cursor.execute('''
INSERT INTO Administration (id, password, role)
VALUES (?, ?, ?)
ON CONFLICT(id) DO NOTHING
''', (0, hashed_password, 'HR'))

# 提交更改并关闭连接
conn.commit()
conn.close()