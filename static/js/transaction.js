const transactionTable = document.getElementById('transaction-table');
const error_message_field = document.getElementById('error-message');

const ethereumButton = document.querySelector('.enableEthereumButton');
const showAccount = document.querySelector('.showAccount');
const showNetwork = document.querySelector('.showNetwork');

ethereumButton.addEventListener('click', () => {
  login();
});

const provider = web3.currentProvider;
myWeb3 = new Web3(provider);

async function login() {
    const accounts = await ethereum.request({ method: 'eth_requestAccounts' });
    const account = accounts[0];
    if (account) {


        fetch('/user?wallet_address=' + account, {
    		method: 'GET',
    	})
    	.then(response => response.json())
    	.then(data => {
    		if (data['success'] === true) {

    			nonce = data['nonce'];
                signMessage(account, nonce)

    		} else if (data['success'] === false) {

                alert("We encountered an error. Please try again.");
    		}
    	})
    	.catch((error) => {
    		console.log('Error: ', error);
    	});
    }

}

async function getChainId() {
	const chainId = ethereum.chainId;

	if (chainId === '0x1') {
		showNetwork.innerHTML = 'Mainnet';
	} else if (chainId === '0x4') {
		showNetwork.innerHTML = 'Rinkeby';
	} else {
		showNetwork.innerHTML = 'Not Mainnet or Rinkeby!';
	}
}

async function signMessage(_account, _nonce) {

    myWeb3.eth.personal.sign(_nonce, _account)
    .then(signedMessage => {

        fetch('/user?wallet_address=' + _account + "&msg=" + signedMessage, {
    		method: 'POST',
    	})
    	.then(response => response.json())
    	.then(data => {
    		if (data['success'] === true) {

                ethereumButton.disabled = true;
        	    ethereumButton.innerHTML = 'Connected';
                showAccount.innerHTML = _account;

                getChainId();
                getTransactions();

    		} else if (data['success'] === false) {

                alert(data['message']);
    		}
    	})
    	.catch((error) => {
    		console.log('Error: ', error);
    	})

    })
    .catch((error) => {
        alert("We encountered an error. Please try again.");
    });
}

async function getTransactions() {

    fetch('/user/transactions', {
        method: 'POST',
        credentials: 'include',
    })
    .then(response => response.json())
    .then(data => {
        if (data['success'] === true) {

            console.log(data);

			var transactions = data['transactions']

			for (let i=0; i<transactions.length; i++) {

				addTransactionRecordToTable(
					transactions[i]['trading_pair'],
					transactions[i]['timestamp'],
					transactions[i]['short_ratio'],
					transactions[i]['current_ratio'],
					transactions[i]['profit_loss']
				)
			}

        } else if (data['success'] === false) {

            alert(data['message']);
        }
    })
    .catch((error) => {
        console.log('Error: ', error);
    })
}


function addTransaction() {
	transaction_hash = document.getElementById('transaction-hash').value;
	console.log(transaction_hash);

	const data = {
		'transaction_hash': transaction_hash
	}

	fetch('/trade/add', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
		},
		body: JSON.stringify(data),
	})
	.then(response => response.json())
	.then(data => {
		if (data['success'] === true) {

			error_message_field.innerHTML = '';

			addTransactionRecordToTable(
				data['trading_pair'],
				data['timestamp'],
				data['short_ratio'],
				data['current_ratio'],
				data['profit_loss']
			)
		} else if (data['success'] === false) {

			error_message_field.innerHTML = data['message'];
		}
	})
	.catch((error) => {
		console.log('Error: ', error);
	});
}

async function addTransactionRecordToTable(_pair, _timestamp, _shortRatio, _currentRatio, _profitLoss) {

	var row = transactionTable.insertRow();

	var td1 = document.createElement('td');
	td1.innerHTML = _pair;
	row.appendChild(td1);

	var td2 = document.createElement('td');
	td2.innerHTML = _timestamp;
	row.appendChild(td2);

	var td3 = document.createElement('td');
	td3.innerHTML = _shortRatio;
	row.appendChild(td3);

	var td4 = document.createElement('td');
	td4.innerHTML = _currentRatio;
	row.appendChild(td4);

	var td5 = document.createElement('td');
	td5.innerHTML = _profitLoss;
	row.appendChild(td5);

}
