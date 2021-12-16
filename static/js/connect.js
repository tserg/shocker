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
