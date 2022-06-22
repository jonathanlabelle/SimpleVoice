import sqlalchemy
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from sqlalchemy.orm import sessionmaker, scoped_session

from forms import LogInForm, SignupForm, CreateClientForm, EditClientGetIDForm, EditClientInformationForm, \
    CreateInvoiceForm, EditInvoiceGetIDForm, EditInvoiceInformationForm, CreateItemForm, EditItemGetIDForm, \
    EditItemInformationForm, CreateInvoiceLines, EditInvoiceLineGetIDForm, EditInvoiceLineInformation

from model import app, db, create_db, Users, Clients, Invoices, Items, InvoicesLines
from utils import check_if_item_exist, get_item_info


#TODO INSERTS SAME ITEMS INVOICE LINES

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


@app.route('/create_invoice', methods=['POST', 'GET'])
@login_required
def create_invoice():
    form = CreateInvoiceForm()
    if form.validate_on_submit():
        client_id = form.client_id.data
        client_data = Clients.query.filter_by(client_id=client_id).first()
        if client_data.user == current_user.id:
            invoice = Invoices(client_id=client_id, total=0, user=current_user.id)
            session.add(invoice)
            session.commit()
            print(invoice.invoice_id)
            flash('Added invoice number {} for {}(id: {})'.format(invoice.invoice_id, client_data.name,
                                                                  client_data.client_id))
        session.commit()
        return redirect(url_for('create_invoice'))
    return render_template('create_invoice.html', form=form)


@app.route('/edit_invoice', methods=['POST', 'GET'])
@login_required
def edit_invoice_get_id():
    form = EditInvoiceGetIDForm()
    if form.validate_on_submit():
        invoice = Invoices.query.filter_by(invoice_id=form.invoice_id.data).first()
        if invoice.user == current_user.id:
            return redirect(url_for('edit_invoice_information', invoice_id=form.invoice_id.data))
        else:
            flash("Invoice {} doesn't exists".format(form.invoice_id.data))
    return render_template('edit_invoice.html', form=form)


@app.route('/edit_invoice_information', methods=['POST', 'GET'])
@login_required
def edit_invoice_information():
    invoice_id = int(request.args.get('invoice_id'))
    invoice = Invoices.query.filter_by(invoice_id=invoice_id).first()
    form = EditInvoiceInformationForm()
    if request.method == 'GET':
        return render_template('edit_invoice_information.html', invoice=invoice, form=form,
                               current_client='current client : {}'.format(invoice.client_id))
    if form.validate_on_submit():
        return redirect(url_for('home'))


@app.route('/edit_invoice_information_update/<invoice_id>', methods=['POST'])
@login_required
def edit_invoice_information_update(invoice_id):
    invoice = Invoices.query.filter_by(invoice_id=invoice_id).first()
    form = EditInvoiceInformationForm()
    if form.client_id.data:
        invoice.client_id = form.client_id.data
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/create_item', methods=['POST', 'GET'])
@login_required
def create_item():
    form = CreateItemForm()
    if form.validate_on_submit():
        item = Items(item_name=form.item_name.data, item_price=form.item_price.data, user=current_user.id)
        session.add(item)
        session.commit()
        return redirect(url_for('home'))
    return render_template('create_item.html', form=form)


@app.route('/edit_item', methods=['POST', 'GET'])
@login_required
def edit_item_get_id():
    form = EditItemGetIDForm()
    if form.validate_on_submit():
        item = Items.query.filter_by(item_id=form.item_id.data).first()
        if item.user == current_user.id:
            return redirect(url_for('edit_item_information', item_id=item.item_id))
        else:
            flash("Item {} doesn't exists".format(form.item_id.data))
    return render_template('edit_item.html', form=form)


@app.route('/edit_item_information', methods=['POST', 'GET'])
@login_required
def edit_item_information():
    item_id = int(request.args.get('item_id'))
    item = Items.query.filter_by(item_id=item_id).first()
    form = EditItemInformationForm()
    if request.method == 'GET':
        return render_template('edit_item_information.html', item=item, form=form)
    if form.validate_on_submit():
        return redirect(url_for('home'))


@app.route('/edit_item_information_update/<item_id>', methods=['POST'])
@login_required
def edit_item_information_update(item_id):
    item = Items.query.filter_by(item_id=item_id).first()
    form = EditItemInformationForm()
    if form.item_name.data:
        item.item_name = form.item_name.data
    if form.item_price.data:
        item.item_price = form.item_price.data
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/create_invoice_line', methods=['POST', 'GET'])
@login_required
def create_invoice_line():
    form = CreateInvoiceLines()
    if form.validate_on_submit():
        invoice = Invoices.query.filter_by(invoice_id=form.invoice_id.data).first()
        if invoice.user == current_user.id:
            if check_if_item_exist(form.item_id_1.data, current_user.id) and form.quantity_1.data > 0:
                item_info = get_item_info(form.item_id_1.data)
                invoice_line_1 = InvoicesLines(invoice_id=form.invoice_id.data, item_id=form.item_id_1.data,
                                               item_name=item_info[0], price=item_info[1],
                                               quantity=form.quantity_1.data, user=current_user.id)
                session.add(invoice_line_1)
                session.commit()
                flash('First line successfully added')
            else:
                flash('Problem adding first line')
            if form.item_id_2.data:
                if check_if_item_exist(form.item_id_2.data, current_user.id) and form.quantity_2.data > 0:
                    item_info = get_item_info(form.item_id_2.data)
                    invoice_line_2 = InvoicesLines(invoice_id=form.invoice_id.data, item_id=form.item_id_2.data,
                                                   item_name=item_info[0], price=item_info[1],
                                                   quantity=form.quantity_2.data, user=current_user.id)
                    session.add(invoice_line_2)
                    session.commit()
                    flash('Second line successfully added')
                else:
                    flash('Problem adding second line')
            if form.item_id_3.data:
                if check_if_item_exist(form.item_id_3.data, current_user.id) and form.quantity_3.data > 0:
                    item_info = get_item_info(form.item_id_3.data)
                    invoice_line_3 = InvoicesLines(invoice_id=form.invoice_id.data, item_id=form.item_id_3.data,
                                                   item_name=item_info[0], price=item_info[1],
                                                   quantity=form.quantity_3.data, user=current_user.id)
                    session.add(invoice_line_3)
                    session.commit()
                    flash('Third line successfully added')
                else:
                    flash('Problem adding third line')
            return redirect(url_for('create_invoice_line'))
        else:
            flash("Invoice doesn't exist")
    return render_template('create_invoice_line.html', form=form)


@app.route('/edit_invoice_line', methods=['POST', 'GET'])
@login_required
def edit_invoice_line_get_id():
    form = EditInvoiceLineGetIDForm()
    if form.validate_on_submit():
        invoice_line = InvoicesLines.query.filter_by(item_id=form.item_id.data, invoice_id=form.invoice_id.data).first()
        if invoice_line.user == current_user.id:
            return redirect(url_for('edit_invoice_line_information', item_id=form.item_id.data,
                                    invoice_id=form.invoice_id.data))
        else:
            flash("Invoice line doesn't exists".format(form.item_id.data))
    return render_template('edit_invoice_line.html', form=form)


@app.route('/edit_invoice_line_information', methods=['POST', 'GET'])
@login_required
def edit_invoice_line_information():
    item_id = int(request.args.get('item_id'))
    invoice_id = int(request.args.get('invoice_id'))
    invoice_line = InvoicesLines.query.filter_by(item_id=item_id, invoice_id=invoice_id).first()
    form = EditInvoiceLineInformation()
    if request.method == 'GET':
        return render_template('edit_invoice_line_information.html', invoice_line=invoice_line, form=form)
    if form.validate_on_submit():
        return redirect(url_for('home'))


@app.route('/edit_invoice_line_information_update/<invoice_id>&<item_id>', methods=['POST'])
@login_required
def edit_invoice_line_information_update(invoice_id, item_id):
    invoice_line = InvoicesLines.query.filter_by(item_id=item_id, invoice_id=invoice_id).first()
    form = EditInvoiceLineInformation()
    if form.item_name.data:
        invoice_line.item_name = form.item_name.data
    if form.quantity.data:
        invoice_line.quantity = form.quantity.data
    if form.item_price.data:
        invoice_line.price = form.item_price.data
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/test', methods=['POST'])
@login_required
def test():
    form = EditClientInformationForm()
    name = form.clientName.data
    return render_template('test.html', name=name)


if __name__ == '__main__':
    create_db()