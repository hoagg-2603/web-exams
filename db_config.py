import sqlite3
import os

# Lấy đường dẫn thư mục hiện tại của file db_config.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, 'database.db')

def get_db():
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db = get_db()
    # Bảng người dùng
    db.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE, password TEXT, fullname TEXT, role TEXT)''')

    # Bảng danh mục Tên kỳ thi
    db.execute('CREATE TABLE IF NOT EXISTS exam_names (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)')

    # Bảng câu hỏi
    db.execute('''CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT,
        a TEXT, b TEXT, c TEXT, d TEXT, ans TEXT)''')

    # Bảng lịch thi
    db.execute('''CREATE TABLE IF NOT EXISTS exams (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name_id INTEGER,
        start_time DATETIME, duration INTEGER, num_questions INTEGER DEFAULT 10,
        FOREIGN KEY(name_id) REFERENCES exam_names(id))''')

    # Bảng kết quả
    db.execute('''CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
        exam_id INTEGER, score REAL,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(exam_id) REFERENCES exams(id))''')
    db.commit()