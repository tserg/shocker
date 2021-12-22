import os

from dotenv import load_dotenv

from sqlalchemy.schema import UniqueConstraint
from flask_sqlalchemy import SQLAlchemy

from flask_migrate import Migrate

from random import randint

load_dotenv()

database_path = os.getenv('DATABASE_URL')

db = SQLAlchemy()

def setup_db(app, database_path=database_path):

    app.config['SQLALCHEMY_DATABASE_URI'] = database_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.app = app
    db.init_app(app)
    db.create_all()
    migrate = Migrate(app, db)

def random_nonce():
    return str(randint(1000000, 9999999))

class User(db.Model):

    __tablename__ = 'users'

    wallet_address = db.Column(
        db.String,
        primary_key=True,
    )

    nonce = db.Column(
        db.String,
        nullable=False,
        default=random_nonce,
    )

    def insert(self):

        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Transaction(db.Model):

    __tablename__ = 'transactions'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    user_address = db.Column(
        db.String,
        db.ForeignKey('users.wallet_address'),
        nullable=False
    )

    tx_hash = db.Column(
        db.String,
        nullable=False
    )

    trading_pair = db.Column(
        db.String,
        nullable=False,
    )

    opened_on = db.Column(
        db.DateTime,
        nullable=False,
    )

    short_ratio = db.Column(
        db.Float,
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint('user_address', 'tx_hash'),
    )

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
