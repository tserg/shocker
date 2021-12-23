import re

from web3 import Web3

def is_transaction_valid(tx_hash) -> bool:
    pattern = re.compile(r"^0x[a-fA-F0-9]{64}")
    return bool(re.fullmatch(pattern, tx_hash))

def calculate_profit_loss(
    to_token_amount,
    from_token_amount,
    current_ratio
):
    return Web3.fromWei(
        int(to_token_amount) - (int(from_token_amount) * current_ratio),
        'ether'
    )
