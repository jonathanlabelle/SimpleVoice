
import flask
import flask_login
import sqlalchemy as sqlalchemy
from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy

from model import Users, Base, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField


app = Flask(__name__)
app.secret_key = b'11d6841a9bbad1f9e44d19b03fb911a7fa8de044e7f3e1ae506827793088992c'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        user = Users.query.filter_by(username=username).first()
        login_user(user)
        return redirect(url_for('home'))
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return "logged out"


@app.route('/index')
@login_required
def home():
    user = flask_login.current_user
    return render_template('home.html', user=user)


def info():
    user = Users(username='vice', password='pattes')
    session.add(user)
    Users.add(user)
    session.commit()
    user = Users.query.filter_by(id=id).first()
    print(user.username)


if __name__ == '__main__':
    user = Users.query.filter_by(id=1).first()
    print(user)

