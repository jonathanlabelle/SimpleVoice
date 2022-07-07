from ensurepip import bootstrap

import sqlalchemy
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, Column, VARCHAR, ForeignKey, Numeric, PrimaryKeyConstraint, ForeignKeyConstraint
from flask_login import UserMixin
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config['SECRET_KEY'] = b'11d6841a9bbad1f9e44d19b03fb911a7fa8de044e7f3e1ae506827793088992c'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/heroku_b1ce9c50c117bec'
# engine = sqlalchemy.create_engine('mysql://root:root@localhost/heroku_b1ce9c50c117bec')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://bbdbc6ed170c04:8e7b1bf4@us-cdbr-east-06.cleardb.net/heroku_b1ce9c50c117bec'
app.config['MYSQL_DATABASE_USER'] = 'bbdbc6ed170c04'
app.config['MYSQL_DATABASE_PASSWORD'] = '8e7b1bf4'
app.config['MYSQL_DATABASE_DB'] = 'heroku_b1ce9c50c117bec'
app.config['MYSQL_DATABASE_HOST'] = 'us-cdbr-east-06.cleardb.net'
app.config['SQLALCHEMY_POOL_RECYCLE']  = 60
app.config['SQLALCHEMY_POOL_TIMEOUT'] = 60
app.config['SQLALCHEMY_PRE_PING'] = True
engine = sqlalchemy.create_engine('mysql://bbdbc6ed170c04:8e7b1bf4@us-cdbr-east-06.cleardb.net/heroku_b1ce9c50c117bec',
                                  pool_recycle=60, pool_pre_ping=True, pool_size=10)
db = SQLAlchemy(app)
db.init_app(app)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = scoped_session(Session)
Bootstrap(app)

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
    item_id = db.Column(db.Integer, nullable=False, autoincrement=True)
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
    item_id = db.Column(db.Integer)
    item_name = db.Column(db.VARCHAR(length=100))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Numeric(7, 2))
    user = db.Column(db.Integer, ForeignKey("Users.id"))

    _table_args__ = (
        ForeignKeyConstraint(['invoice_id', 'client_id', 'user'],
                             ['Invoices.invoice_id', 'Clients.client_id', 'Users.id']),
        PrimaryKeyConstraint(invoice_id, item_id, user),
    )


"""
trigger_insert_invoice_line_total = "CREATE TRIGGER insert_invoice_line_total_trigger AFTER INSERT ON invoices_lines " \
                                    "FOR EACH ROW UPDATE invoices I SET total =(SELECT SUM(quantity*price) " \
                                    "FROM invoices_lines IL WHERE I.invoice_id = IL.invoice_id) " \
                                    "WHERE I.invoice_id = New.invoice_id;"

trigger_update_invoice_line_total = "CREATE TRIGGER update_invoice_line_total_trigger AFTER UPDATE ON invoices_lines " \
                                    "FOR EACH ROW UPDATE invoices I SET total =(SELECT SUM(quantity*price) " \
                                    "FROM invoices_lines IL WHERE I.invoice_id = IL.invoice_id) " \
                                    "WHERE I.invoice_id = New.invoice_id;"

trigger_delete_invoice_line_total = "CREATE TRIGGER delete_invoice_line_total_trigger AFTER DELETE ON invoices_lines " \
                                    "FOR EACH ROW UPDATE invoices I SET total =(SELECT SUM(quantity*price) " \
                                    "FROM invoices_lines IL WHERE I.invoice_id = IL.invoice_id) " \
                                    "WHERE I.invoice_id = OLD.invoice_id;"
"""


def create_db():
    #engine = sqlalchemy.create_engine('mysql://root:root@localhost')
    engine.execute("CREATE DATABASE IF NOT EXISTS heroku_b1ce9c50c117bec;")
    engine.execute("USE heroku_b1ce9c50c117bec;")
    db.create_all()
    db.session.commit()

