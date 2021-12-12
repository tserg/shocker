import os
import json
import requests

from datetime import datetime

from dotenv import load_dotenv

from flask import (
    Flask,
    jsonify,
    request,
    render_template,
)

from web3 import Web3

from utils import is_transaction_valid

load_dotenv()

app = Flask(__name__)

INFURA_PROJECT_ID = os.getenv('INFURA_PROJECT_ID')
INFURA_SECRET = os.getenv('INFURA_SECRET')

UNISWAP_V3_ROUTER_ADDRESS = os.getenv('UNISWAP_V3_ROUTER_ADDRESS')
UNISWAP_V3_GRAPH_API_URL = os.getenv('UNISWAP_V3_GRAPH_API_URL')

with open("contracts/ERC20ABI.json") as f:
    erc20_json = json.load(f)

ERC20ABI = erc20_json

@app.route('/', methods=['GET'])
def index():
    return render_template('pages/index.html')

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

        w3 = Web3(Web3.HTTPProvider(f'https://mainnet.infura.io/v3/{INFURA_PROJECT_ID}'))

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
