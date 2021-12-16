import os
import json
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
)

from flask_sqlalchemy import SQLAlchemy

from web3 import Web3

from utils import is_transaction_valid

from models import (
    random_nonce,
    setup_db,
    User,
)

load_dotenv()

def create_app():
    app = Flask(__name__)
    db = SQLAlchemy()

    setup_db(app)

    INFURA_PROJECT_ID = os.getenv('INFURA_PROJECT_ID')
    INFURA_SECRET = os.getenv('INFURA_SECRET')

    UNISWAP_V3_ROUTER_ADDRESS = os.getenv('UNISWAP_V3_ROUTER_ADDRESS')
    UNISWAP_V3_GRAPH_API_URL = os.getenv('UNISWAP_V3_GRAPH_API_URL')

    w3 = Web3(Web3.HTTPProvider(f'https://mainnet.infura.io/v3/{INFURA_PROJECT_ID}'))

    with open("contracts/ERC20ABI.json") as f:
        erc20_json = json.load(f)

    ERC20ABI = erc20_json

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

                print("Old nonce: " + str(nonce))
                print("New nonce: " + str(user.nonce))

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

        try:

            tx_receipt = w3.eth.get_transaction_receipt(tx_hash)

            if tx_receipt.to.lower() != UNISWAP_V3_ROUTER_ADDRESS.lower():

                return jsonify({
                    'success': False,
                    'message': 'The transaction is not a Uniswap V3 transaction.'
                })

            to_token_log = tx_receipt.logs[0]
            to_token_address = to_token_log.address
            to_token_amount = int(to_token_log.data, 16)
            to_token_contract = w3.eth.contract(
                address=to_token_address,
                abi=ERC20ABI
            )
            to_token_symbol = to_token_contract.functions.symbol().call()

            from_token_log = tx_receipt.logs[1]
            from_token_address = from_token_log.address
            from_token_amount = int(from_token_log.data, 16)
            from_token_contract = w3.eth.contract(
                address=from_token_address,
                abi=ERC20ABI
            )
            from_token_symbol = from_token_contract.functions.symbol().call()


            block_number = tx_receipt.blockNumber
            tx_timestamp = datetime.utcfromtimestamp(
                int(w3.eth.get_block(block_number).timestamp)
            ).strftime('%Y-%m-%d %H:%M:%S')

            trading_pair = from_token_symbol + "-" + to_token_symbol
            short_ratio = to_token_amount / from_token_amount

            query = '''{
                token(id: "''' +  str(from_token_address).lower() + '''") {
                    derivedETH
                }
            }'''

            current_ratio = 0
            try:

                response = requests.post(
                    url=UNISWAP_V3_GRAPH_API_URL,
                    headers={
                        "Content-Type": "application/json"
                    },
                    json={"query": query}
                )

                response_data = response.text

                start_idx = response_data.find('"derivedETH":"')
                end_idx = response_data.find('"', start_idx+14)

                current_ratio = float(response_data[start_idx+14:end_idx])
                profit_loss = Web3.fromWei(to_token_amount - (from_token_amount * current_ratio), 'ether')

            except Exception as e:
                print(e)
                return jsonify({
                    'success': False,
                    'message': 'We encountered an issue while trying to retrieve the transaction. Please try again.'
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

    return app
