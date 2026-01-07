import sqlite3

def get_db():
    conn = sqlite3.connect('database.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db = get_db()
    db.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE, password TEXT, fullname TEXT, role TEXT)''')
    db.execute('CREATE TABLE IF NOT EXISTS classes (id INTEGER PRIMARY KEY, name TEXT)')
    db.execute('''CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT, 
        a TEXT, b TEXT, c TEXT, d TEXT, ans TEXT)''')
    # Thêm cột num_questions
    db.execute('''CREATE TABLE IF NOT EXISTS exams (
        id INTEGER PRIMARY KEY AUTOINCREMENT, class_id INTEGER, 
        start_time DATETIME, duration INTEGER, num_questions INTEGER DEFAULT 10,
        FOREIGN KEY(class_id) REFERENCES classes(id))''')
    db.execute('''CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, 
        exam_id INTEGER, score REAL, 
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(exam_id) REFERENCES exams(id))''')
    db.execute('INSERT OR IGNORE INTO classes (id, name) VALUES (1, "Lớp CNTT 01"), (2, "Lớp CNTT 02")')
    db.commit()