from flask import Flask, make_response, request, render_template, session, redirect, abort
from flask_login import login_user, login_required, logout_user, current_user
import datetime

from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

from data.works import Works
from data.users import User
from flask_login import LoginManager
from data import db_session
from main import main
from forms.works import WorksLogForm
from forms.user import RegisterForm

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/")
def index():
    db_sess = db_session.create_session()
    works = db_sess.query(Works)
    return render_template("index.html", works=works)


@app.route('/works', methods=['GET', 'POST'])
@login_required
def add_works():
    form = WorksLogForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        works = Works()
        works.title_of_activity = form.title.data
        works.team_leader = form.team_leader.data
        works.is_finished = form.is_finished.data
        works.collaborators = form.collaborators.data
        works.work_size = form.work_size.data
        current_user.works.append(works)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('works.html', title='Добавление новости',
                           form=form)


@app.route('/works/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_works(id):
    form = WorksLogForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        works = db_sess.query(Works).filter(Works.id == id, Works.user == current_user).first()
        if works:
            form.title.data = works.title_of_activity
            form.team_leader.data = works.team_leader
            form.is_finished.data = works.is_finished
            form.collaborators.data = works.collaborators
            form.work_size.data = works.work_size
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        works = db_sess.query(Works).filter(Works.id == id, Works.user == current_user).first()
        if works:
            works.title_of_activity = form.title.data
            works.team_leader = form.team_leader.data
            works.is_finished = form.is_finished.data
            form.collaborators.data = works.collaborators
            form.work_size.data = works.work_size
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('works.html',
                           title='Редактирование новости',
                           form=form
                           )


@app.route('/works_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def works_delete(id):
    db_sess = db_session.create_session()
    works = db_sess.query(Works).filter(Works.id == id, Works.user == current_user).first()
    if works:
        db_sess.delete(works)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


if __name__ == '__main__':
    main()
    app.run(port=8080, host='127.0.0.1', debug=True)
