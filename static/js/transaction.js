const transactionTable = document.getElementById('transaction-table');

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

			addTransactionRecordToTable(
				data['trading_pair'],
				data['timestamp'],
				data['short_ratio'],
				data['current_ratio'],
				data['profit_loss']
			)
		} else if (data['success'] === false) {
			error_message_field = document.getElementById('error-message');
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
