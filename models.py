import os

from dotenv import load_dotenv

from sqlalchemy.schema import UniqueConstraint
from flask_sqlalchemy import SQLAlchemy

from flask_migrate import Migrate

from random import randint

from utils.transaction import calculate_profit_loss
from utils.fetchers.uniswap_v3_fetcher import get_uniswap_v3_price

load_dotenv()

database_path = os.getenv('DATABASE_URL')

if database_path.startswith("postgres://"):
    database_path = database_path.replace('postgres://', 'postgresql://', 1)

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

    def get_transactions(self):

        transactions = Transaction.query.filter(
            Transaction.user_address==self.wallet_address
        ).all()

        transaction_data = []

        for t in transactions:
            t_data = t.to_dict()
            current_ratio = get_uniswap_v3_price(
                t_data['from_token_address']
            )
            t_data['current_ratio'] = current_ratio
            t_data['profit_loss'] = calculate_profit_loss(
                t_data['to_token_amount'],
                t_data['from_token_amount'],
                current_ratio
            )
            transaction_data.append(t_data)

        return transaction_data


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

    to_token_amount = db.Column(
        db.Numeric,
        nullable=False,
    )

    from_token_amount = db.Column(
        db.Numeric,
        nullable=False,
    )

    from_token_address = db.Column(
        db.String,
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint('user_address', 'tx_hash'),
    )

    def to_dict(self):

        data = {
            'tx_hash': self.tx_hash,
            'trading_pair': self.trading_pair,
            'timestamp': self.opened_on,
            'short_ratio': self.short_ratio,
            'to_token_amount': self.to_token_amount,
            'from_token_amount': self.from_token_amount,
            'from_token_address': self.from_token_address,
        }

        return data

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
