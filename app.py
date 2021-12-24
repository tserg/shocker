import os
import requests

from datetime import datetime

from dotenv import load_dotenv

from eth_account import (
    Account,
)

from eth_account.messages import (
    encode_defunct
)

from flask import (
    Flask,
    jsonify,
    request,
    render_template,
    session,
)

from flask_sqlalchemy import SQLAlchemy

from web3 import Web3

from utils.transaction import (
    is_transaction_valid,
    calculate_profit_loss,
)

from models import (
    random_nonce,
    setup_db,
    User,
    Transaction,
)

from utils.fetchers.uniswap_v3_fetcher import (
    get_uniswap_v3_price,
)

from utils.router import (
    is_supported_swap,
    get_transaction_info,
)

load_dotenv()

INFURA_PROJECT_ID = os.getenv('INFURA_PROJECT_ID')
INFURA_SECRET = os.getenv('INFURA_SECRET')

UNISWAP_V3_GRAPH_API_URL = os.getenv('UNISWAP_V3_GRAPH_API_URL')

SECRET_KEY = os.getenv('SECRET_KEY')

def create_app():
    app = Flask(__name__)
    db = SQLAlchemy()

    setup_db(app)

    app.secret_key = SECRET_KEY

    w3 = Web3(Web3.HTTPProvider(f'https://mainnet.infura.io/v3/{INFURA_PROJECT_ID}'))

    @app.route('/', methods=['GET'])
    def index():
        return render_template('pages/index.html')

    @app.route('/user', methods=['GET', 'POST'])
    def login():

        if request.method == 'GET':

            try:

                wallet_address = request.args.get('wallet_address')
                user = User.query.filter(
                    User.wallet_address==wallet_address
                ).first()

                if not user:
                    user = User(
                        wallet_address=wallet_address
                    )
                    user.insert()

                return jsonify({
                    'success': True,
                    'nonce': user.nonce
                })

            except Exception as e:

                print(e)

                return jsonify({
                    'success': False,
                })

        elif request.method == 'POST':

            try:

                signed_message = request.args.get('msg')

                wallet_address = request.args.get('wallet_address')
                user = User.query.filter(
                    User.wallet_address==wallet_address
                ).first()

                nonce = user.nonce
                message = encode_defunct(text=nonce)


                recovered_address = Account.recover_message(message, signature=signed_message)

                if wallet_address.lower() != recovered_address.lower():

                    return jsonify({
                        'success': False,
                        'message': 'We are unable to verify the signed message.'
                    })

                user.nonce = random_nonce()
                user.update()

                session['wallet_address'] = wallet_address
                print(session)

                return jsonify({
                    'success': True
                })

            except Exception as e:

                print(e)

                return jsonify({
                    'success': False
                })

            return jsonify({
                'success': False
            })


    @app.route('/trade/add', methods=['POST'])
    def add_trade():

        data = request.get_json()
        tx_hash = data['transaction_hash']

        if not is_transaction_valid(tx_hash):
            return jsonify({
                'success': False,
                'message': 'Transaction hash is invalid.'
            })

        is_user = False
        if 'wallet_address' in session:

            user = User.query.filter(
                User.wallet_address==session['wallet_address']
            ).first()
            if user:
                is_user = True

        try:

            tx_receipt = w3.eth.get_transaction_receipt(tx_hash)

            swap_address = tx_receipt.to.lower()

            if not is_supported_swap(swap_address):

                return jsonify({
                    'success': False,
                    'message': 'We currently do not support transactions with this provider.'
                })

            from_token_address, from_token_amount, to_token_amount, tx_timestamp, \
                trading_pair, short_ratio = get_transaction_info(w3, swap_address, tx_receipt)

            current_ratio = 0
            try:

                current_ratio = get_uniswap_v3_price(from_token_address)
                profit_loss = calculate_profit_loss(
                    to_token_amount,
                    from_token_amount,
                    current_ratio
                )

            except Exception as e:
                print(e)
                return jsonify({
                    'success': False,
                    'message': 'We encountered an issue while trying to retrieve the transaction. Please try again.'
                })

            if is_user:

                tx = Transaction.query.filter(
                    Transaction.tx_hash==tx_hash,
                    Transaction.user_address==user.wallet_address,
                ).first()

                if not tx:

                    try:
                        transaction = Transaction(
                            user_address=user.wallet_address,
                            tx_hash=tx_hash,
                            trading_pair=trading_pair,
                            opened_on=tx_timestamp,
                            short_ratio=short_ratio,
                            to_token_amount=to_token_amount,
                            from_token_amount=from_token_amount,
                            from_token_address=from_token_address,
                        )
                        transaction.insert()

                    except Exception as e:
                        print(e)

                else:
                    return jsonify({
                        'success': False,
                        'message': 'This transaction has already been added.'
                    })

            return jsonify({
                'success': True,
                'trading_pair': trading_pair,
                'timestamp': tx_timestamp,
                'short_ratio': short_ratio,
                'current_ratio': current_ratio,
                'profit_loss': profit_loss,
            })

        except:

            return jsonify({
                'success': False,
                'message': 'We encountered an issue while trying to retrieve the transaction. Please try again.'
            })

    @app.route('/user/transactions', methods=['POST'])
    def get_transactions():

        wallet_address = session['wallet_address']

        user = User.query.filter(
            User.wallet_address==wallet_address
        ).first()

        if not user:

            return jsonify({
                'success': False,
                'message': f'You are not authorised to view the transactions for {wallet_address}.'
            })

        transaction_data = user.get_transactions()

        return jsonify({
            'success': True,
            'transactions': transaction_data
        })

    return app

app = create_app()
