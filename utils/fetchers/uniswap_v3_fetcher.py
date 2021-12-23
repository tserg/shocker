import os
import json
import requests

from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

UNISWAP_V3_ROUTER_ADDRESS = os.getenv('UNISWAP_V3_ROUTER_ADDRESS')
UNISWAP_V3_GRAPH_API_URL = os.getenv('UNISWAP_V3_GRAPH_API_URL')

with open("contracts/ERC20ABI.json") as f:
    erc20_json = json.load(f)

ERC20ABI = erc20_json

def get_uniswap_v3_transaction_info(w3, tx_receipt):

    print("uniswap fetcher triggered")
    print(tx_receipt)

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

    print("from token")

    block_number = tx_receipt.blockNumber
    tx_timestamp = datetime.utcfromtimestamp(
        int(w3.eth.get_block(block_number).timestamp)
    ).strftime('%Y-%m-%d %H:%M:%S')

    trading_pair = from_token_symbol + "-" + to_token_symbol
    short_ratio = to_token_amount / from_token_amount

    return from_token_address, \
        from_token_amount, \
        to_token_amount, \
        tx_timestamp, \
        trading_pair, \
        short_ratio

def get_uniswap_v3_price(
    from_token_address
):

    query = '''{
        token(id: "''' +  str(from_token_address).lower() + '''") {
            derivedETH
        }
    }'''

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

    return current_ratio
