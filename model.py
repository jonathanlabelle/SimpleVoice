import sqlalchemy
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, Column, VARCHAR, ForeignKey, Numeric, PrimaryKeyConstraint, ForeignKeyConstraint
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = b'11d6841a9bbad1f9e44d19b03fb911a7fa8de044e7f3e1ae506827793088992c'
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/SimpleVoice'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)


class Users(UserMixin, db.Model):
    __tablename__ = "Users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.VARCHAR(100), nullable=False, unique=True)
    companyName = db.Column(db.VARCHAR(200), nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(
            password,
            method='sha256'
        )

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Clients(db.Model):
    __tablename__ = "Clients"
    client_id = db.Column(db.Integer, autoincrement=True)
    name = db.Column(db.VARCHAR(length=255))
    phone = db.Column(db.VARCHAR(length=10))
    email = db.Column(db.VARCHAR(length=255))
    reference = db.Column(db.VARCHAR(length=100))
    user = db.Column(db.Integer, ForeignKey("Users.id"))

    _table_args__ = (
        ForeignKeyConstraint(['user'], ['Users.id']),
        PrimaryKeyConstraint(client_id, user)
    )


class Invoices(db.Model):
    __tablename__ = "Invoices"
    invoice_id = Column(Integer, autoincrement=True)
    client_id = Column(Integer, ForeignKey("Clients.client_id"))
    total = Column(Numeric(7, 2))
    user = Column(Integer, ForeignKey("Users.id"))

    _table_args__ = (
        ForeignKeyConstraint(['client_id', 'user'], ['Clients.client_id', 'Users.id']),
        PrimaryKeyConstraint(invoice_id, client_id, user),
    )


class Items(db.Model):
    __tablename__ = "Items"
    item_id = db.Column(db.Integer, nullable=False)
    item_name = db.Column(db.VARCHAR(length=100), nullable=False)
    item_price = db.Column(db.Numeric(7, 2), nullable=False)
    user = db.Column(db.Integer, ForeignKey("Users.id"))

    _table_args__ = (
        ForeignKeyConstraint(['user'], ['Users.id']),
        PrimaryKeyConstraint(item_id, user),
    )


class InvoicesLines(db.Model):
    __tablename__ = "Invoices_lines"
    invoice_id = db.Column(db.Integer, ForeignKey("Invoices.invoice_id"))
    client_id = db.Column(db.Integer, ForeignKey("Clients.client_id"))
    name = db.Column(db.VARCHAR(length=100))
    item_id = db.Column(db.Integer)
    quantity = db.Column(db.Integer)
    price = db.Column(db.Numeric(7, 2))
    user = db.Column(db.Integer, ForeignKey("Users.id"))

    _table_args__ = (
        ForeignKeyConstraint(['invoice_id', 'client_id', 'user'],
                             ['Invoices.invoice_id', 'Clients.client_id', 'Users.id']),
        PrimaryKeyConstraint(invoice_id, item_id, user),
    )


def create_db():
    engine = sqlalchemy.create_engine('mysql://root:root@localhost')  # connect to server
    engine.execute("CREATE DATABASE IF NOT EXISTS simplevoice;")
    engine.execute("USE simplevoice;")
    db.create_all()
    db.session.commit()

