from flask import Blueprint, render_template, request, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from db_config import get_db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        db = get_db()
        pwd = generate_password_hash(request.form['password'])
        db.execute('INSERT INTO users (username, password, fullname, role) VALUES (?, ?, ?, ?)',
                   (request.form['username'], pwd, request.form['fullname'], request.form['role']))
        db.commit()
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = get_db().execute('SELECT * FROM users WHERE username = ?', (request.form['username'],)).fetchone()
        if user and check_password_hash(user['password'], request.form['password']):
            session.update({'user_id': user['id'], 'fullname': user['fullname'], 'role': user['role']})
            return redirect(url_for('index'))
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))