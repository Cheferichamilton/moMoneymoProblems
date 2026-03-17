import sqlite3
from sqlite3 import Connection
from datetime import datetime, timedelta

def get_connection() -> Connection:
    conn = sqlite3.connect('budget.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()
    # Categories
    cur.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')
    # Transactions
    cur.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            amount REAL NOT NULL,
            category_id INTEGER,
            description TEXT,
            FOREIGN KEY(category_id) REFERENCES categories(id)
        )
    ''')
    # Recurring bills
    cur.execute('''
        CREATE TABLE IF NOT EXISTS recurring (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            amount REAL NOT NULL,
            category_id INTEGER,
            frequency TEXT NOT NULL,
            next_due TEXT NOT NULL,
            FOREIGN KEY(category_id) REFERENCES categories(id)
        )
    ''')
    # Pay schedule
    # Incomes table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS incomes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            amount REAL NOT NULL,
            frequency TEXT NOT NULL,
            next_due TEXT NOT NULL
        )
    ''')
    # Incomes table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS incomes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            amount REAL NOT NULL,
            frequency TEXT NOT NULL,
            next_due TEXT NOT NULL
        )
    ''')
    # Incomes table
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS incomes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            amount REAL NOT NULL,
            frequency TEXT NOT NULL,
            next_due TEXT NOT NULL
        )
        '''
    )

    cur.execute('''
        CREATE TABLE IF NOT EXISTS pay_schedule (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            pay_amount REAL NOT NULL,
            pay_frequency TEXT NOT NULL,
            next_pay_date TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Category operations
def get_categories():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM categories')
    rows = cur.fetchall()
    conn.close()
    return rows

def add_category(name: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('INSERT OR IGNORE INTO categories (name) VALUES (?)', (name,))
    conn.commit()
    conn.close()

# Transaction operations
def add_transaction(date: str, amount: float, category_id: int = None, description: str = ''):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO transactions (date, amount, category_id, description) VALUES (?, ?, ?, ?)',
        (date, amount, category_id, description)
    )
    conn.commit()
    conn.close()

def get_transactions(start_date=None, end_date=None):
    conn = get_connection()
    cur = conn.cursor()
    sql = 'SELECT t.*, c.name as category FROM transactions t LEFT JOIN categories c ON t.category_id = c.id'
    params = []
    if start_date and end_date:
        sql += ' WHERE date BETWEEN ? AND ?'
        params = [start_date, end_date]
    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    return rows

# Recurring bills

def add_recurring(name: str, amount: float, category_id: int = None, frequency: str = 'monthly', next_due: str = None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO recurring (name, amount, category_id, frequency, next_due) VALUES (?, ?, ?, ?, ?)',
        (name, amount, category_id, frequency, next_due)
    )
    conn.commit()
    conn.close()

def get_recurring():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT r.*, c.name as category FROM recurring r LEFT JOIN categories c ON r.category_id = c.id')
    rows = cur.fetchall()
    conn.close()
    return rows

# Pay schedule

def get_pay_schedule():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM pay_schedule WHERE id = 1')
    row = cur.fetchone()
    conn.close()
    return row

def set_pay_schedule(pay_amount: float, pay_frequency: str, next_pay_date: str):
    """Upsert single pay schedule entry (id=1)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        '''
        INSERT INTO pay_schedule (id, pay_amount, pay_frequency, next_pay_date)
        VALUES (1, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            pay_amount=excluded.pay_amount,
            pay_frequency=excluded.pay_frequency,
            next_pay_date=excluded.next_pay_date;
        ''',
        (pay_amount, pay_frequency, next_pay_date)
    )
    conn.commit()
    conn.close()

# Advance recurring bill due date
def update_recurring_next_due(recurring_id: int, current_due: str):
    """
    After marking a recurring bill paid, bump its next_due based on frequency.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT frequency FROM recurring WHERE id = ?', (recurring_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return
    freq = row['frequency']
    due_date = datetime.fromisoformat(current_due).date()
    mapping = {
        'daily': timedelta(days=1),
        'weekly': timedelta(weeks=1),
        'biweekly': timedelta(weeks=2),
        'monthly': timedelta(days=30)
    }
    delta = mapping.get(freq, timedelta(days=30))
    new_due = due_date + delta
    cur.execute('UPDATE recurring SET next_due = ? WHERE id = ?', (new_due.isoformat(), recurring_id))
    conn.commit()
    conn.close()

# Income operations
def add_income(name: str, amount: float, frequency: str, next_due: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO incomes (name, amount, frequency, next_due) VALUES (?, ?, ?, ?)',
        (name, amount, frequency, next_due)
    )
    conn.commit()
    conn.close()

def get_incomes():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM incomes')
    rows = cur.fetchall()
    conn.close()
    return rows

def update_income(income_id: int, name: str, amount: float, frequency: str, next_due: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        'UPDATE incomes SET name=?, amount=?, frequency=?, next_due=? WHERE id=?',
        (name, amount, frequency, next_due, income_id)
    )
    conn.commit()
    conn.close()

def delete_income(income_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM incomes WHERE id=?', (income_id,))
    conn.commit()
    conn.close()
def update_recurring_next_due(recurring_id: int, current_due: str):
    """
    After marking a recurring bill paid, bump its next_due based on frequency.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT frequency FROM recurring WHERE id = ?', (recurring_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return
    freq = row['frequency']
    due_date = datetime.fromisoformat(current_due).date()
    mapping = {
        'daily': timedelta(days=1),
        'weekly': timedelta(weeks=1),
        'biweekly': timedelta(weeks=2),
        'monthly': timedelta(days=30)
    }
    delta = mapping.get(freq, timedelta(days=30))
    new_due = due_date + delta
    cur.execute('UPDATE recurring SET next_due = ? WHERE id = ?', (new_due.isoformat(), recurring_id))
    conn.commit()
    conn.close()
