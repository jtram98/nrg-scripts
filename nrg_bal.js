const Web3 = require('web3');
const web3Extension = require('@energi/web3-ext');
 
const web3 = new Web3('https://nodeapi.energi.network');
 
// extend the features of web3, so that you have Energi's full public api:
web3Extension.extend(web3);
 
// use web3 for json-rpc requests:
const showBalance = async address => {
    let balance, balanceWei, balanceNrg;
    try {
        balance = await web3.nrg.getBalance(address);
 
        // balance is a BigNumber. To show, use .toString():
        balanceWei = balance.toString();
        balanceNrg = web3.utils.fromWei(balanceWei, 'nrg');
        process.stdout.write(balanceNrg); 
    }
    catch (err) {
        console.error(err);
    }
};
 
const myAddress =  process.env.NRG_ADDR;
 
showBalance(myAddress);