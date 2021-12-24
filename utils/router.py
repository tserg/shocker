import os
import json

from dotenv import load_dotenv

from utils.fetchers.metamask_fetcher import (
    get_metamask_transaction_info,
)

from utils.fetchers.uniswap_v3_fetcher import (
    get_uniswap_v3_transaction_info,
)

load_dotenv()

UNISWAP_V3_ROUTER_ADDRESS = os.getenv('UNISWAP_V3_ROUTER_ADDRESS')
METAMASK_ROUTER_ADDRESS = os.getenv('METAMASK_ROUTER_ADDRESS')

with open("contracts/ERC20ABI.json") as f:
    erc20_json = json.load(f)

ERC20ABI = erc20_json

def is_supported_swap(swap_address):

    if swap_address in [
        UNISWAP_V3_ROUTER_ADDRESS,
        METAMASK_ROUTER_ADDRESS,
    ]:

        return True

    return False

def get_transaction_info(w3, swap_address, tx_receipt):

    if swap_address == UNISWAP_V3_ROUTER_ADDRESS:

        return get_uniswap_v3_transaction_info(w3, tx_receipt, ERC20ABI)

    elif swap_address == METAMASK_ROUTER_ADDRESS:

        return get_metamask_transaction_info(w3, tx_receipt, ERC20ABI)
