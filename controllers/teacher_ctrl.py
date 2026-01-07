from flask import Blueprint, render_template, request, redirect, url_for, session
from db_config import get_db

teacher_bp = Blueprint('teacher', __name__, url_prefix='/teacher')

@teacher_bp.route('/questions', methods=['GET', 'POST'])
def manage_questions():
    db = get_db()
    if request.method == 'POST':
        db.execute('INSERT INTO questions (content, a, b, c, d, ans) VALUES (?, ?, ?, ?, ?, ?)',
                   (request.form['content'], request.form['a'], request.form['b'], 
                    request.form['c'], request.form['d'], request.form['ans']))
        db.commit()
    questions = db.execute('SELECT * FROM questions').fetchall()
    return render_template('teacher/questions.html', questions=questions)

@teacher_bp.route('/questions/edit/<int:id>', methods=['GET', 'POST'])
def edit_question(id):
    db = get_db()
    if request.method == 'POST':
        db.execute('''UPDATE questions SET content=?, a=?, b=?, c=?, d=?, ans=? WHERE id=?''',
                   (request.form['content'], request.form['a'], request.form['b'], 
                    request.form['c'], request.form['d'], request.form['ans'], id))
        db.commit()
        return redirect(url_for('teacher.manage_questions'))
    
    question = db.execute('SELECT * FROM questions WHERE id = ?', (id,)).fetchone()
    return render_template('teacher/edit_question.html', q=question)

@teacher_bp.route('/questions/delete/<int:id>')
def delete_question(id):
    db = get_db()
    db.execute('DELETE FROM questions WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('teacher.manage_questions'))

@teacher_bp.route('/classes')
def manage_classes():
    db = get_db()
    classes = db.execute('SELECT * FROM classes').fetchall()
    exams = db.execute('''SELECT exams.*, classes.name as class_name 
                          FROM exams JOIN classes ON exams.class_id = classes.id''').fetchall()
    return render_template('teacher/classes.html', classes=classes, exams=exams)

@teacher_bp.route('/schedule_exam', methods=['POST'])
def schedule_exam():
    db = get_db()
    dt = f"{request.form['date']} {request.form['time']}"
    db.execute('INSERT INTO exams (class_id, start_time, duration, num_questions) VALUES (?, ?, ?, ?)',
               (request.form['class_id'], dt, request.form['duration'], request.form['num_questions']))
    db.commit()
    return redirect(url_for('teacher.manage_classes'))

# Bước 1: Chọn lớp muốn xem kết quả
@teacher_bp.route('/results')
def select_class_results():
    if 'user_id' not in session or session.get('role') != 'teacher':
         return redirect(url_for('auth.login'))

    db = get_db()
    classes = db.execute('SELECT * FROM classes').fetchall()
    return render_template('teacher/select_class_results.html', classes=classes)

# Bước 2: Hiển thị kết quả chi tiết của lớp đã chọn
@teacher_bp.route('/results/<int:class_id>')
def view_specific_class_results(class_id):
    db = get_db()
    selected_class = db.execute('SELECT * FROM classes WHERE id = ?', (class_id,)).fetchone()
    if not selected_class:
        return "Lớp không tồn tại!", 404

    results = db.execute('''
        SELECT results.score, users.fullname as student_name, exams.start_time
        FROM results
        JOIN users ON results.user_id = users.id
        JOIN exams ON results.exam_id = exams.id
        WHERE exams.class_id = ?
        ORDER BY exams.start_time DESC, users.fullname ASC
    ''', (class_id,)).fetchall()

    return render_template('teacher/class_results_detail.html',
                           results=results,
                           selected_class=selected_class)