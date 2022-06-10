import sqlalchemy
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from sqlalchemy.orm import sessionmaker, scoped_session

from forms import LogInForm, SignupForm

from model import app, db, create_db, Users

engine = sqlalchemy.create_engine('mysql://root:root@localhost/SimpleVoice')
login_manager = LoginManager()
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = scoped_session(Session)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


@app.route('/', methods=['GET', 'POST'])
def login():
    form = LogInForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.loginName.data).first()
        if user and user.check_password(password=form.password.data):
            login_user(user)
            return redirect(url_for('home'))
        flash('invalid username/password combination')
    return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        username = form.loginName.data
        existing_user = session.query(Users).filter_by(username=username).first()
        if existing_user is None:
            user = Users(username=form.loginName.data, companyName=form.companyName.data)
            user.set_password(form.password.data)
            session.add(user)
            session.commit()
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('User ' + form.loginName.data + ' already exists')
    return render_template('signup.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return "logged out"


@app.route('/index')
@login_required
def home():
    user = current_user
    return render_template('home.html', user=user)


if __name__ == '__main__':
    create_db()

