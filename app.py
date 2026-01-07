from flask import Flask, session, redirect, url_for
from db_config import init_db
from controllers.auth_ctrl import auth_bp
from controllers.teacher_ctrl import teacher_bp
from controllers.student_ctrl import student_bp

app = Flask(__name__)
app.secret_key = 'secret_key_123'

# Khởi tạo DB
init_db()

# Đăng ký Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(teacher_bp)
app.register_blueprint(student_bp)

@app.route('/')
def index():
    if 'user_id' not in session: return redirect(url_for('auth.login'))
    return redirect(url_for('teacher.manage_classes') if session['role'] == 'teacher' else url_for('student.list_exams'))

if __name__ == '__main__':
    app.run(debug=True)