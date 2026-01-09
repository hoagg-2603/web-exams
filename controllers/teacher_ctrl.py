from flask import Blueprint, render_template, request, redirect, url_for, session
from db_config import get_db

teacher_bp = Blueprint('teacher', __name__, url_prefix='/teacher')

# --- 1. QUẢN LÝ CÂU HỎI ---
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

# --- 2. QUẢN LÝ DANH MỤC TÊN KỲ THI ---
@teacher_bp.route('/exam-names', methods=['GET', 'POST'])
def manage_exam_names():
    db = get_db()
    if request.method == 'POST':
        name = request.form.get('name')
        db.execute('INSERT INTO exam_names (name) VALUES (?)', (name,))
        db.commit()
    names = db.execute('SELECT * FROM exam_names').fetchall()
    return render_template('teacher/exam_names.html', names=names)

@teacher_bp.route('/exam-names/delete/<int:id>')
def delete_exam_name(id):
    db = get_db()
    db.execute('DELETE FROM exam_names WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('teacher.manage_exam_names'))

# --- 3. LẬP LỊCH THI (Fix BuildError tại đây) ---
@teacher_bp.route('/schedule')
def manage_schedule(): # Tên hàm phải là manage_schedule để khớp với app.py
    db = get_db()
    exam_names = db.execute('SELECT * FROM exam_names').fetchall()
    exams = db.execute('''SELECT exams.*, exam_names.name as exam_display_name 
                          FROM exams JOIN exam_names ON exams.name_id = exam_names.id''').fetchall()
    return render_template('teacher/classes.html', exam_names=exam_names, exams=exams)

@teacher_bp.route('/schedule_exam', methods=['POST'])
def schedule_exam():
    db = get_db()
    dt = f"{request.form['date']} {request.form['time']}"
    db.execute('INSERT INTO exams (name_id, start_time, duration, num_questions) VALUES (?, ?, ?, ?)',
               (request.form['name_id'], dt, request.form['duration'], request.form['num_questions']))
    db.commit()
    return redirect(url_for('teacher.manage_schedule'))

# --- 4. XEM KẾT QUẢ THI ---
@teacher_bp.route('/results')
def select_exam_results():
    if 'user_id' not in session or session.get('role') != 'teacher':
         return redirect(url_for('auth.login'))

    db = get_db()
    # Hiển thị các kỳ thi thực tế đã được xếp lịch
    scheduled_exams = db.execute('''
        SELECT exams.id, exam_names.name, exams.start_time 
        FROM exams 
        JOIN exam_names ON exams.name_id = exam_names.id
        ORDER BY exams.start_time DESC
    ''').fetchall()
    return render_template('teacher/select_class_results.html', exams=scheduled_exams)

@teacher_bp.route('/results/<int:exam_id>')
def view_exam_detail(exam_id):
    db = get_db()
    exam_info = db.execute('''
        SELECT exams.id, exam_names.name, exams.start_time 
        FROM exams 
        JOIN exam_names ON exams.name_id = exam_names.id
        WHERE exams.id = ?''', (exam_id,)).fetchone()
    
    if not exam_info:
        return "Kỳ thi không tồn tại!", 404

    results = db.execute('''
        SELECT results.score, users.fullname as student_name
        FROM results
        JOIN users ON results.user_id = users.id
        WHERE results.exam_id = ?
        ORDER BY users.fullname ASC
    ''', (exam_id,)).fetchall()

    return render_template('teacher/class_results_detail.html',
                           results=results,
                           exam=exam_info)