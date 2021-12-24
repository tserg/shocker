import requests

from datetime import datetime

def get_metamask_transaction_info(w3, tx_receipt, erc20abi):

    print("metamask fetcher triggered")
    print(tx_receipt)

    to_token_log = tx_receipt.logs[2]
    to_token_address = to_token_log.address
    to_token_amount = int(to_token_log.data, 16)
    to_token_contract = w3.eth.contract(
        address=to_token_address,
        abi=erc20abi
    )
    to_token_symbol = to_token_contract.functions.symbol().call()

    from_token_log = tx_receipt.logs[0]
    from_token_address = from_token_log.address
    from_token_amount = int(from_token_log.data, 16)
    from_token_contract = w3.eth.contract(
        address=from_token_address,
        abi=erc20abi
    )
    from_token_symbol = from_token_contract.functions.symbol().call()

    print("from token")

    block_number = tx_receipt.blockNumber
    tx_timestamp = datetime.utcfromtimestamp(
        int(w3.eth.get_block(block_number).timestamp)
    )

    trading_pair = from_token_symbol + "-" + to_token_symbol
    short_ratio = to_token_amount / from_token_amount

    return from_token_address, \
        from_token_amount, \
        to_token_amount, \
        tx_timestamp, \
        trading_pair, \
        short_ratio
