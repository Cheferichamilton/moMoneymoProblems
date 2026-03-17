import sqlite3
from sqlite3 import Connection

def get_connection() -> Connection:
    conn = sqlite3.connect('budget.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()
    # Categories table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')
    # Transactions (both one-time and individual occurrences)
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
    # Pay schedule (one row only)
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

# Helper functions

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


def add_transaction(date: str, amount: float, category_id: int, description: str = ''):
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
    query = 'SELECT t.*, c.name as category FROM transactions t LEFT JOIN categories c ON t.category_id = c.id'
    params = []
    if start_date and end_date:
        query += ' WHERE date BETWEEN ? AND ?'
        params = [start_date, end_date]
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return rows


def add_recurring(name: str, amount: float, category_id: int, frequency: str, next_due: str):
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


def get_pay_schedule():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM pay_schedule WHERE id = 1')
    row = cur.fetchone()
    conn.close()
    return row


def set_pay_schedule(pay_amount: float, pay_frequency: str, next_pay_date: str):
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
