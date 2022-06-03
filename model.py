import sqlalchemy
from sqlalchemy import Integer, Column, VARCHAR, ForeignKey, Numeric, PrimaryKeyConstraint, ForeignKeyConstraint, insert
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

engine = sqlalchemy.create_engine('mysql://root:root@localhost/SimpleVoice')
engine.execute("USE SimpleVoice")
Base = declarative_base()
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = scoped_session(Session)
Base.query = session.query_property()

from . import db


class Users(UserMixin, db.Model):
    __tablename__ = "Users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.VARCHAR(100), nullable=False, unique=True)
    password = db.Column(db.VARCHAR(200), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(
            password,
            method='sha256'
        )

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Clients(Base):
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


class Invoices(Base):
    __tablename__ = "Invoices"
    invoice_id = Column(Integer)
    client_id = Column(Integer, ForeignKey("Clients.client_id"))
    total = Column(Numeric(7, 2))
    user = Column(Integer, ForeignKey("Users.id"))

    _table_args__ = (
        ForeignKeyConstraint(['client_id', 'user'], ['Clients.client_id', 'Users.id']),
        PrimaryKeyConstraint(invoice_id, client_id, user),
    )


class Items(Base):
    __tablename__ = "Items"
    item_id = db.Column(db.Integer, nullable=False)
    item_name = db.Column(db.VARCHAR(length=100), nullable=False)
    item_price = db.Column(db.Numeric(7, 2), nullable=False)
    user = db.Column(db.Integer, ForeignKey("Users.id"))

    _table_args__ = (
        ForeignKeyConstraint(['user'], ['Users.id']),
        PrimaryKeyConstraint(item_id, user),
    )


class InvoicesLines(Base):
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


if __name__ == '__main__':
    engine.execute("DROP DATABASE SimpleVoice")
    engine.execute("CREATE DATABASE SimpleVoice")
    Base.metadata.create_all(engine)
    #engine.execute("DROP DATABASE SimpleVoice")
