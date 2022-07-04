import sqlalchemy
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from sqlalchemy import desc
from sqlalchemy.orm import sessionmaker, scoped_session

from forms import LogInForm, SignupForm, CreateClientForm, GetIDClientForm, EditClientInformationForm, \
    CreateInvoiceForm, GetIDInvoiceForm, EditInvoiceInformationForm, CreateItemForm, GetIDItemForm, \
    EditItemInformationForm, CreateInvoiceLines, GetInvoiceLineIDForm, EditInvoiceLineInformation, ConfirmationForm

from model import db, create_db, Users, Clients, Invoices, Items, InvoicesLines, app
from utils import check_if_item_exist, get_item_info


app.config['SECRET_KEY'] = b'11d6841a9bbad1f9e44d19b03fb911a7fa8de044e7f3e1ae506827793088992c'
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/SimpleVoice'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
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


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('login'))


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
        flash("New client created with ID number {}".format(client.client_id))
        return redirect(url_for('create_client'))
    return render_template('create_client.html', form=form, user=current_user)


@app.route('/delete_client', methods=['GET', 'POST'])
@login_required
def delete_client():
    form = GetIDClientForm()
    if form.validate_on_submit():
        client_id = form.client_id.data
        client = Clients.query.filter_by(client_id=client_id).first()
        if client:
            if client.user == current_user.id:
                return redirect(url_for('delete_client_confirmation', client_id=client_id))
        else:
            flash('Client does not exist')
    return render_template('delete_client.html', form=form, user=current_user)


@app.route('/delete_client_confirmation', methods=['GET', 'POST'])
@login_required
def delete_client_confirmation():
    message = "Safe to delete, no invoices associated with the client"
    client_id = int(request.args.get('client_id'))
    client = Clients.query.filter_by(client_id=client_id).first()
    if Invoices.query.filter_by(client_id=client_id).first():
        message = "Caution: Client still has invoices, they will be deleted if the client is deleted"
    form = ConfirmationForm()
    return render_template('delete_client_confirmation.html', client=client, form=form, message=message,
                           user=current_user)


@app.route('/delete_client_confirmation_delete/<client_id>', methods=['POST'])
@login_required
def delete_client_confirmation_delete(client_id):
    client = Clients.query.filter_by(client_id=client_id).first()
    if client.user == current_user.id:
        invoices = Invoices.query.filter_by(client_id=client_id).all()
        if invoices:
            for invoice in invoices:
                invoice_lines = InvoicesLines.query.filter_by(invoice_id=invoice.invoice_id).all()
                if invoice_lines:
                    for invoice_line in invoice_lines:
                        db.session.delete(invoice_line)
                        db.session.commit()
                db.session.delete(invoice)
                db.session.commit()
        db.session.delete(client)
        db.session.commit()
        flash('Client deleted')
    else:
        flash('Problem deleting the client')
    return redirect(url_for('home'))


@app.route('/edit_client_get_id', methods=['POST', 'GET'])
@login_required
def edit_client_get_id():
    form = GetIDClientForm()
    if form.validate_on_submit():
        client = Clients.query.filter_by(client_id=form.client_id.data).first()
        if client:
            if client.user == current_user.id:
                return redirect(url_for('edit_client_information', client_id=form.client_id.data))
        else:
            flash("Client {} doesn't exists".format(form.client_id.data))
    return render_template('edit_client.html', form=form, user=current_user)


@app.route('/edit_client_information', methods=['POST', 'GET'])
@login_required
def edit_client_information():
    client_id = int(request.args.get('client_id'))
    client = Clients.query.filter_by(client_id=client_id).first()
    form = EditClientInformationForm()
    if request.method == 'GET':
        return render_template('edit_client_information.html', client=client, client_id=client_id, form=form,
                               user=current_user)
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
    flash("Client {} updated".format(client.client_id))
    return redirect(url_for('home'))


@app.route('/create_invoice', methods=['POST', 'GET'])
@login_required
def create_invoice():
    form = CreateInvoiceForm()
    if form.validate_on_submit():
        client_id = form.client_id.data
        client_data = Clients.query.filter_by(client_id=client_id).first()
        if client_data:
            if client_data.user == current_user.id:
                invoice = Invoices(client_id=client_id, total=0, user=current_user.id)
                session.add(invoice)
                session.commit()
                print(invoice.invoice_id)
                flash('Added invoice number {} for {}(id: {})'.format(invoice.invoice_id, client_data.name,
                                                                      client_data.client_id))
                session.commit()
        else:
            flash('No client matching that id')
        return redirect(url_for('create_invoice'))
    return render_template('create_invoice.html', form=form, user=current_user)


@app.route('/edit_invoice', methods=['POST', 'GET'])
@login_required
def edit_invoice_get_id():
    invoices = session.query(Invoices, Clients.name).join(Clients).filter_by(user=current_user.id).all()
    form = GetIDInvoiceForm()
    if form.validate_on_submit():
        invoice = Invoices.query.filter_by(invoice_id=form.invoice_id.data).first()
        if invoice.user == current_user.id:
            return redirect(url_for('edit_invoice_information', invoice_id=form.invoice_id.data))
        else:
            flash("Invoice {} doesn't exists".format(form.invoice_id.data))
    return render_template('edit_invoice.html', form=form, user=current_user, invoices=invoices)


@app.route('/edit_invoice_information', methods=['POST', 'GET'])
@login_required
def edit_invoice_information():
    invoice_id = int(request.args.get('invoice_id'))
    invoice = Invoices.query.filter_by(invoice_id=invoice_id).first()
    form = EditInvoiceInformationForm()
    if request.method == 'GET':
        return render_template('edit_invoice_information.html', invoice=invoice, form=form,
                               current_client='current client : {}'.format(invoice.client_id), user=current_user)
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


@app.route('/delete_invoice', methods=['GET', 'POST'])
@login_required
def delete_invoice():
    invoices = session.query(Invoices, Clients.name).join(Clients).filter_by(user=current_user.id).all()
    form = GetIDInvoiceForm()
    if form.validate_on_submit():
        invoice_id = form.invoice_id.data
        invoice = Invoices.query.filter_by(invoice_id=invoice_id).first()
        if invoice:
            if invoice.user == current_user.id:
                return redirect(url_for('delete_invoice_confirmation', invoice_id=invoice_id))
        else:
            flash('Invoice does not exist')
    return render_template('delete_invoice.html', form=form, user=current_user, invoices=invoices)


@app.route('/delete_invoice_confirmation', methods=['GET', 'POST'])
@login_required
def delete_invoice_confirmation():
    message = "Safe to delete, invoice is empty"
    invoice_id = int(request.args.get('invoice_id'))
    invoice = Invoices.query.filter_by(invoice_id=invoice_id).first()
    if InvoicesLines.query.filter_by(invoice_id=invoice_id).first():
        message = "Caution: Invoice is not empty, all lines will be deleted"
    form = ConfirmationForm()
    return render_template('delete_invoice_confirmation.html', invoice=invoice, form=form, message=message,
                           user=current_user)


@app.route('/delete_invoice_confirmation_delete/<invoice_id>', methods=['POST'])
@login_required
def delete_invoice_confirmation_delete(invoice_id):
    invoice = Invoices.query.filter_by(invoice_id=invoice_id).first()
    if invoice.user == current_user.id:
        invoice_lines = InvoicesLines.query.filter_by(invoice_id=invoice_id).all()
        if invoice_lines:
            for invoice_line in invoice_lines:
                db.session.delete(invoice_line)
                db.session.commit()
        db.session.delete(invoice)
        db.session.commit()
        flash('Invoice deleted')
    else:
        flash('Problem deleting the invoice')
    return redirect(url_for('home'))


@app.route('/create_item', methods=['POST', 'GET'])
@login_required
def create_item():
    form = CreateItemForm()
    if form.validate_on_submit():
        item = Items(item_name=form.item_name.data, item_price=form.item_price.data, user=current_user.id)
        session.add(item)
        session.commit()
        flash("{} created with ID {}".format(item.item_name, item.item_id))
        return redirect(url_for('home'))
    return render_template('create_item.html', form=form, user=current_user)


@app.route('/edit_item', methods=['POST', 'GET'])
@login_required
def edit_item_get_id():
    items = Items.query.filter_by(user=current_user.id).order_by('item_name').all()
    form = GetIDItemForm()
    if form.validate_on_submit():
        item = Items.query.filter_by(item_id=form.item_id.data).first()
        if item and item.user == current_user.id:
            return redirect(url_for('edit_item_information', item_id=item.item_id))
        else:
            flash("Item {} doesn't exists".format(form.item_id.data))
    return render_template('edit_item.html', form=form, user=current_user, items=items)


@app.route('/edit_item_information', methods=['POST', 'GET'])
@login_required
def edit_item_information():
    item_id = int(request.args.get('item_id'))
    item = Items.query.filter_by(item_id=item_id).first()
    form = EditItemInformationForm()
    if request.method == 'GET':
        return render_template('edit_item_information.html', item=item, form=form, user=current_user)
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
    flash("Item edited")
    return redirect(url_for('home'))


@app.route('/delete_item', methods=['GET', 'POST'])
@login_required
def delete_item():
    items = Items.query.filter_by(user=current_user.id).order_by('item_name').all()
    form = GetIDItemForm()
    if form.validate_on_submit():
        item_id = form.item_id.data
        item = Items.query.filter_by(item_id=item_id).first()
        if item:
            if item.user == current_user.id:
                return redirect(url_for('delete_item_confirmation', item_id=item_id))
        else:
            flash('Item does not exist')
    return render_template('delete_item.html', form=form, user=current_user, items=items)


@app.route('/delete_item_confirmation', methods=['GET', 'POST'])
@login_required
def delete_item_confirmation():
    item_id = int(request.args.get('item_id'))
    item = Items.query.filter_by(item_id=item_id).first()
    form = ConfirmationForm()
    return render_template('delete_item_confirmation.html', item=item, form=form, user=current_user)


@app.route('/delete_item_confirmation_delete/<item_id>', methods=['POST'])
@login_required
def delete_item_confirmation_delete(item_id):
    item = Items.query.filter_by(item_id=item_id).first()
    if item.user == current_user.id:
        db.session.delete(item)
        db.session.commit()
        flash('Item deleted')
    else:
        flash('Problem deleting the item')
    return redirect(url_for('home'))


@app.route('/create_invoice_line', methods=['POST', 'GET'])
@login_required
def create_invoice_line():
    invoices = session.query(Invoices, Clients.name).join(Clients).filter_by(user=current_user.id)\
        .order_by(desc(Invoices.invoice_id)).limit(20).all()
    form = CreateInvoiceLines()
    if form.validate_on_submit():
        invoice = Invoices.query.filter_by(invoice_id=form.invoice_id.data).first()
        if invoice:
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
    return render_template('create_invoice_line.html', invoices=invoices, form=form, user=current_user)


@app.route('/edit_invoice_line', methods=['POST', 'GET'])
@login_required
def edit_invoice_line_get_id():
    invoices = session.query(Invoices, Clients.name).join(Clients).filter_by(user=current_user.id)\
        .order_by(desc(Invoices.invoice_id)).limit(20).all()
    form = GetInvoiceLineIDForm()
    if form.validate_on_submit():
        invoice_line = InvoicesLines.query.filter_by(item_id=form.item_id.data, invoice_id=form.invoice_id.data).first()
        if invoice_line:
            if invoice_line.user == current_user.id:
                return redirect(url_for('edit_invoice_line_information', item_id=form.item_id.data,
                                        invoice_id=form.invoice_id.data))
        else:
            flash("Invoice line doesn't exists".format(form.item_id.data))
    return render_template('edit_invoice_line.html', invoices=invoices, form=form, user=current_user)


@app.route('/edit_invoice_line_information', methods=['POST', 'GET'])
@login_required
def edit_invoice_line_information():
    item_id = int(request.args.get('item_id'))
    invoice_id = int(request.args.get('invoice_id'))
    invoice_line = InvoicesLines.query.filter_by(item_id=item_id, invoice_id=invoice_id).first()
    form = EditInvoiceLineInformation()
    if request.method == 'GET':
        return render_template('edit_invoice_line_information.html', invoice_line=invoice_line, form=form,
                               user=current_user)
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
    flash("Invoice line updated")
    return redirect(url_for('home'))


@app.route('/delete_invoice_line', methods=['GET', 'POST'])
@login_required
def delete_invoice_line():
    invoices = session.query(Invoices, Clients.name).join(Clients).filter_by(user=current_user.id).all()
    form = GetInvoiceLineIDForm()
    if form.validate_on_submit():
        invoice_id = form.invoice_id.data
        item_id = form.item_id.data
        invoice_line = InvoicesLines.query.filter_by(item_id=item_id, invoice_id=invoice_id).first()
        if invoice_line:
            if invoice_line.user == current_user.id:
                return redirect(url_for('delete_invoice_line_confirmation', invoice_id=invoice_id, item_id=item_id))
        else:
            flash('Invoice line does not exist')
    return render_template('delete_invoice_line.html', invoices=invoices, form=form, user=current_user)


@app.route('/delete_invoice_line_confirmation', methods=['GET', 'POST'])
@login_required
def delete_invoice_line_confirmation():
    item_id = int(request.args.get('item_id'))
    invoice_id = int(request.args.get('invoice_id'))
    invoice_line = InvoicesLines.query.filter_by(item_id=item_id, invoice_id=invoice_id).first()
    form = ConfirmationForm()
    if form.validate_on_submit():
        if invoice_line.user == current_user.user:
            db.session.delete(invoice_line)
            db.session.commit()
            return redirect(url_for('home'))
        else:
            flash('Problem deleting the invoice')
    return render_template('delete_invoice_line_confirmation.html', invoice_line=invoice_line, form=form,
                           user=current_user)


@app.route('/delete_invoice_line_confirmation_delete/<invoice_id>&<item_id>', methods=['POST'])
@login_required
def delete_invoice_line_information_delete(invoice_id, item_id):
    invoice_line = InvoicesLines.query.filter_by(item_id=item_id, invoice_id=invoice_id).first()
    if invoice_line.user == current_user.id:
        db.session.delete(invoice_line)
        db.session.commit()
        flash('Invoice line deleted')
    else:
        flash('Problem deleting the invoice')
    return redirect(url_for('home'))


@app.route('/view_invoices_last_10', methods=['GET', 'POST'])
@login_required
def view_invoices_last_10():
    invoices = session.query(Invoices, Clients.name).join(Clients).filter_by(user=current_user.id) \
        .order_by(desc(Invoices.invoice_id)).limit(10).all()
    return render_template('view_invoices_list.html', invoices=invoices, user=current_user)


@app.route('/view_invoices_all_invoices', methods=['GET', 'POST'])
@login_required
def view_invoices_all_invoices():
    invoices = session.query(Invoices, Clients.name).join(Clients).filter_by(user=current_user.id).all()
    return render_template('view_invoices_list.html', invoices=invoices, user=current_user)


# session.query(Clients)... check first if the client exist, then check if the client belongs to the user
@app.route('/view_invoices_by_invoice_id', methods=['GET', 'POST'])
@login_required
def view_invoices_by_invoice_id():
    form = GetIDInvoiceForm()
    if form.validate_on_submit():
        if session.query(Invoices).filter_by(invoice_id=form.invoice_id.data).first() and \
                current_user.id == session.query(Invoices.user).filter_by(invoice_id=form.invoice_id.data).first()[0]:
            return redirect(url_for('view_invoice', invoice_id=form.invoice_id.data))
    return render_template('view_invoices_by_id.html', form=form, user=current_user.id)


@app.route('/view_invoices_by_client_id', methods=['GET', 'POST'])
@login_required
def view_invoices_by_client_id():
    form = GetIDClientForm()
    if form.validate_on_submit():
        invoices = session.query(Invoices, Clients.name).join(Clients).filter_by(client_id=form.client_id.data,
                                                                                 user=current_user.id).all()
        return render_template('view_invoices_list.html', invoices=invoices, user=current_user)
    return render_template('view_invoices_by_client_id.html', user=current_user.id, form=form)


@app.route('/view_clients_last_10', methods=['GET', 'POST'])
@login_required
def view_clients_last_10():
    clients = session.query(Clients).filter_by(user=current_user.id).order_by(desc(Clients.client_id)).limit(10).all()
    return render_template('view_clients_list.html', clients=clients, user=current_user)


@app.route('/view_clients_all_clients_id', methods=['GET', 'POST'])
@login_required
def view_clients_all_clients_id():
    clients = session.query(Clients).filter_by(user=current_user.id).all()
    return render_template('view_clients_list.html', clients=clients, user=current_user)


@app.route('/view_clients_all_clients_name', methods=['GET', 'POST'])
@login_required
def view_clients_all_clients_name():
    clients = session.query(Clients).filter_by(user=current_user.id).order_by(Clients.name).all()
    return render_template('view_clients_list.html', clients=clients, user=current_user)


"""
session.query(Clients)... check first if the client exist, then check if the client belongs to the user
"""


@app.route('/view_clients_by_client_id', methods=['GET', 'POST'])
@login_required
def view_clients_by_client_id():
    form = GetIDClientForm()
    if form.validate_on_submit():
        if session.query(Clients).filter_by(client_id=form.client_id.data).first() and \
                current_user.id == session.query(Clients.user).filter_by(client_id=form.client_id.data).first()[0]:
            return redirect(url_for('view_client', client_id=form.client_id.data))
    return render_template('view_clients_by_id.html', form=form, user=current_user.id)


@app.route('/view_items_last_10', methods=['GET', 'POST'])
@login_required
def view_items_last_10():
    items = session.query(Items).filter_by(user=current_user.id).order_by(desc(Items.item_id)).limit(10).all()
    return render_template('view_items_list.html', items=items, user=current_user)


@app.route('/view_items_all_by_item_id', methods=['GET', 'POST'])
@login_required
def view_items_all_items_by_id():
    items = session.query(Items).filter_by(user=current_user.id).all()
    return render_template('view_items_list.html', items=items, user=current_user)


@app.route('/view_items_all_by_item_name', methods=['GET', 'POST'])
@login_required
def view_items_all_items_by_name():
    items = session.query(Items).filter_by(user=current_user.id).order_by(Items.item_name).all()
    return render_template('view_items_list.html', items=items, user=current_user)


"""
session.query(Clients)... check first if the client exist, then check if the client belongs to the user
"""


@app.route('/view_items_by_item_id', methods=['GET', 'POST'])
@login_required
def view_items_by_item_id():
    form = GetIDItemForm()
    if form.validate_on_submit():
        if session.query(Items).filter_by(item_id=form.item_id.data).first() and \
                current_user.id == session.query(Items.user).filter_by(item_id=form.item_id.data).first()[0]:
            return redirect(url_for('view_item', item_id=form.item_id.data))
    return render_template('view_items_by_id.html', form=form, user=current_user.id)


@app.route('/view_invoice/<int:invoice_id>', methods=['GET', 'POST'])
@login_required
def view_invoice(invoice_id):
    invoice = Invoices.query.filter_by(invoice_id=invoice_id).first()
    client = Clients.query.filter_by(client_id=invoice.client_id).first()
    invoice_lines = InvoicesLines.query.filter_by(invoice_id=invoice_id).all()
    return render_template('view_invoice.html', invoice=invoice, client=client, invoice_lines=invoice_lines,
                           user=current_user.id)


@app.route('/view_client/<int:client_id>', methods=['GET', 'POST'])
@login_required
def view_client(client_id):
    client = Clients.query.filter_by(client_id=client_id).first()
    invoices = Invoices.query.filter_by(client_id=client_id).all()
    return render_template('view_client.html', invoices=invoices, client=client, user=current_user.id)


@app.route('/view_item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def view_item(item_id):
    item = Items.query.filter_by(item_id=item_id).first()
    invoice_lines = InvoicesLines.query.filter_by(item_id=item_id).all()
    return render_template('view_item.html', invoice_lines=invoice_lines, item=item, user=current_user.id)


@app.route('/test', methods=['POST'])
@login_required
def test():
    form = EditClientInformationForm()
    name = form.clientName.data
    return render_template('test.html', name=name, user=current_user)


if __name__ == '__main__':
    app.run()
