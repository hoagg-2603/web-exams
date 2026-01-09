from flask import Flask, session, redirect, url_for
from db_config import init_db
from controllers.auth_ctrl import auth_bp
from controllers.teacher_ctrl import teacher_bp
from controllers.student_ctrl import student_bp

app = Flask(__name__)
app.secret_key = 'phim_bi_mat_d97pb'

# Tự động khởi tạo DB khi chạy máy local
with app.app_context():
    init_db()

app.register_blueprint(auth_bp)
app.register_blueprint(teacher_bp)
app.register_blueprint(student_bp)

@app.route('/')
def index():
    if 'user_id' not in session: 
        return redirect(url_for('auth.login'))
    return redirect(url_for('teacher.manage_schedule') if session['role'] == 'teacher' else url_for('student.list_exams'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)