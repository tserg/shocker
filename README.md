# Overview

Track your profit/loss for manual ERC20 shorts against ETH on Uniswap V3. A live instance is deployed [here](https://eth-shocker.herokuapp.com/).

For each trade, we calculate your profit/loss in ETH based on the existing ERC20-ETH ratio vs the ERC20-ETH ratio at the time of the transaction.

Supported contracts:
- Uniswap V3
- Metamask Swap

# Installation

Run `python -m pip install -r requirements.txt`

Dependencies
- Python 3.10
- web3.py 5.25.0
- Flask 2.0.2

# Getting started

Update the example `.env` file with your Infura details.

```
export FLASK_APP=app
flask run
```
