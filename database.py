import sqlite3
import pandas as pd

DB_FILE = 'login_security.db'


def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Create users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT,
            email TEXT,
            phone TEXT,
            failed_attempts INTEGER DEFAULT 0,
            is_locked INTEGER DEFAULT 0
        )
    ''')
    # Create feedback table
    c.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY,
            username TEXT,
            rating INTEGER,
            comment TEXT
        )
    ''')
    conn.commit()

    # Create recovery_requests table
    c.execute('''
        CREATE TABLE IF NOT EXISTS recovery_requests (
            id INTEGER PRIMARY KEY,
            username TEXT,
            issue TEXT,
            status TEXT DEFAULT 'Pending'
        )
    ''')
    conn.commit()
    conn.close()


def submit_recovery_request_to_db(username, issue):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO recovery_requests (username, issue) VALUES (?, ?)", (username, issue))
    conn.commit()
    conn.close()


def get_pending_recovery_requests_from_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM recovery_requests WHERE status = 'Pending'")
    requests = c.fetchall()
    conn.close()
    return requests


def update_recovery_request_status_in_db(request_id, status):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE recovery_requests SET status = ? WHERE id = ?", (status, request_id))
    conn.commit()
    conn.close()


def create_user(username, password, email, phone):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password, email, phone) VALUES (?, ?, ?, ?)",
                  (username, password, email, phone))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def get_user(username):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    return user


def update_user(username, failed_attempts, is_locked):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE users SET failed_attempts = ?, is_locked = ? WHERE username = ?",
              (failed_attempts, is_locked, username))
    conn.commit()
    conn.close()


def submit_feedback_to_db(username, rating, comment):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO feedback (username, rating, comment) VALUES (?, ?, ?)", (username, rating, comment))
    conn.commit()
    conn.close()


def update_user_password(username, new_password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE users SET password = ? WHERE username = ?", (new_password, username))
    conn.commit()
    conn.close()


def get_feedback_from_db():
    conn = sqlite3.connect(DB_FILE)
    try:
        return pd.read_sql_query("SELECT * FROM feedback", conn)
    finally:
        conn.close()
