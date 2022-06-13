import sqlalchemy
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from sqlalchemy.orm import sessionmaker, scoped_session

from forms import LogInForm, SignupForm, CreateClientForm, EditClientGetIDForm, EditClientInformationForm

from model import app, db, create_db, Users, Clients

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
        return redirect(url_for('login'))
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


@app.route('/create_client', methods=['POST', 'GET'])
@login_required
def create_client():
    form = CreateClientForm()
    if form.validate_on_submit():
        client = Clients(name=form.clientName.data, email=form.clientEmail.data,
                         phone=form.clientPhone.data, reference=form.clientReference.data,
                         user=current_user.id)
        session.add(client)
        session.commit()
        return redirect(url_for('home'))
    return render_template('create_client.html', form=form)


@app.route('/edit_client_get_id', methods=['POST', 'GET'])
@login_required
def edit_client_get_id():
    form = EditClientGetIDForm()
    if form.validate_on_submit():
        client = Clients.query.filter_by(client_id=form.clientID.data).first()
        if client.user == current_user.id:
            return redirect(url_for('edit_client_information', client_id=form.clientID.data))
        else:
            flash("Client {} doesn't exists".format(form.clientID.data))
    return render_template('edit_client.html', form=form)


@app.route('/edit_client_information', methods=['POST', 'GET'])
@login_required
def edit_client_information():
    client_id = int(request.args.get('client_id'))
    client = Clients.query.filter_by(client_id=client_id).first()
    form = EditClientInformationForm()
    if request.method == 'GET':
        return render_template('edit_client_information.html', client=client, client_id=client_id, form=form)
    if form.validate_on_submit():
        return redirect(url_for('home'))


@app.route('/edit_client_information_update/<client_id>', methods=['POST'])
@login_required
def edit_client_information_update(client_id):
        client = Clients.query.filter_by(client_id=client_id).first()
        form = EditClientInformationForm()
        if form.clientName.data:
            client.name = form.clientName.data
        if form.clientEmail.data:
            client.email = form.clientEmail.data
        if form.clientPhone.data:
            client.phone = form.clientPhone.data
        if form.clientReference.data:
            client.reference = form.clientReference.data
        db.session.commit()
        return redirect(url_for('home'))


@app.route('/test', methods=['POST'])
@login_required
def test():
    form = EditClientInformationForm()
    name = form.clientName.data
    return render_template('test.html', name=name)


if __name__ == '__main__':
    print('allo')
