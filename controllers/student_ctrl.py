from flask import Blueprint, render_template, request, redirect, session, url_for
from db_config import get_db
from datetime import datetime, timedelta

student_bp = Blueprint('student', __name__, url_prefix='/student')

@student_bp.route('/exams')
def list_exams():
    if 'user_id' not in session: return redirect(url_for('auth.login'))
    db = get_db()
    user_id = session['user_id']
    
    # Đã sửa: Join với exam_names thay vì classes
    exams = db.execute('''
        SELECT exams.*, exam_names.name as exam_display_name,
               (SELECT id FROM results WHERE exam_id = exams.id AND user_id = ?) as taken_id
        FROM exams 
        JOIN exam_names ON exams.name_id = exam_names.id
    ''', (user_id,)).fetchall()
    
    return render_template('student/exams.html', 
                           exams=exams, 
                           now=datetime.now(), 
                           datetime=datetime, 
                           timedelta=timedelta)

@student_bp.route('/take_exam/<int:exam_id>')
def take_exam(exam_id):
    if 'user_id' not in session: return redirect(url_for('auth.login'))
    db = get_db()
    user_id = session['user_id']
    
    check = db.execute('SELECT id FROM results WHERE exam_id = ? AND user_id = ?', 
                       (exam_id, user_id)).fetchone()
    if check:
        return redirect(url_for('student.list_exams'))

    exam = db.execute('SELECT * FROM exams WHERE id = ?', (exam_id,)).fetchone()
    
    start_dt = datetime.strptime(exam['start_time'], '%Y-%m-%d %H:%M')
    end_dt = start_dt + timedelta(minutes=exam['duration'])
    end_time_iso = end_dt.strftime('%Y-%m-%dT%H:%M:%S')

    num = exam['num_questions'] if exam['num_questions'] else 10
    questions = db.execute('SELECT * FROM questions ORDER BY RANDOM() LIMIT ?', (num,)).fetchall()
    
    return render_template('student/do_exam.html', 
                           questions=questions, 
                           exam=exam, 
                           end_time=end_time_iso)

@student_bp.route('/submit', methods=['POST'])
def submit():
    if 'user_id' not in session: return redirect(url_for('auth.login'))
    db = get_db()
    user_id = session['user_id']
    exam_id = request.form.get('exam_id')
    
    check = db.execute('SELECT id FROM results WHERE exam_id = ? AND user_id = ?', 
                       (exam_id, user_id)).fetchone()
    if check:
        return redirect(url_for('student.view_grades'))

    q_ids = [k.split('_')[1] for k in request.form.keys() if k.startswith('q_')]
    correct = 0
    for q_id in q_ids:
        row = db.execute('SELECT ans FROM questions WHERE id = ?', (q_id,)).fetchone()
        if row and request.form.get(f'q_{q_id}') == row['ans']:
            correct += 1
            
    total = len(q_ids)
    score = round((correct / total) * 10, 2) if total > 0 else 0
    
    db.execute('INSERT INTO results (user_id, exam_id, score) VALUES (?, ?, ?)',
               (user_id, exam_id, score))
    db.commit()
    return render_template('student/result.html', score=score, correct=correct, total=total)

@student_bp.route('/grades')
def view_grades():
    if 'user_id' not in session: return redirect(url_for('auth.login'))
    db = get_db()
    # Đã sửa: Join đúng bảng exam_names
    grades = db.execute('''
        SELECT results.score, exams.start_time, exam_names.name as exam_display_name
        FROM results
        JOIN exams ON results.exam_id = exams.id
        JOIN exam_names ON exams.name_id = exam_names.id
        WHERE results.user_id = ? 
        ORDER BY exams.start_time DESC
    ''', (session['user_id'],)).fetchall()
    return render_template('student/grades.html', grades=grades)