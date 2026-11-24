from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User, Note

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-for-study-project'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        login = request.form.get('login', '').strip()
        password = request.form.get('password', '')

        if not login or not password:
            flash('Заполните оба поля')
            return redirect(url_for('register'))

        if User.query.filter_by(login=login).first():
            flash('Пользователь с таким логином уже существует')
            return redirect(url_for('register'))

        user = User(login=login, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        flash('Регистрация прошла успешно! Теперь войдите.')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form.get('login', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(login=login).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))

        flash('Неверный логин или пароль')
        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/notes', methods=['GET', 'POST'])
@login_required
def notes():
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        if content:
            new_note = Note(content=content, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Заметка добавлена!')
        else:
            flash('Текст заметки не может быть пустым')
        return redirect(url_for('notes'))

    user_notes = Note.query.filter_by(user_id=current_user.id).order_by(Note.id.desc()).all()
    return render_template('notes.html', notes=user_notes)


if __name__ == '__main__':
    app.run(debug=True)
