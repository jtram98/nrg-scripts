const Web3 = require('web3');
const web3Extension = require('@energi/web3-ext');
 
// use 'https://nodeapi.test3.energi.network' to connect to the testnet
// use 'https://nodeapi.energi.network' to connect to the mainnet
const web3 = new Web3('https://nodeapi.energi.network');
 
// extend the features of web3, so that you have Energi's full public api:
web3Extension.extend(web3);
 
// use web3 for json-rpc requests:
const showBalance = async address => {
    let balance, balanceWei, balanceNrg;
    try {
        balance = await web3.nrg.getBalance(address);
        colbalance = await web3.masternode.collateralBalance(address)
        mninfo = await web3.masternode.masternodeInfo(address)
 
        // balance is a BigNumber. To show, use .toString():
        balanceWei = balance.toString();
        balanceNrg = web3.utils.fromWei(balanceWei, 'nrg');
        console.log('Balance:', colbalance);
        console.log('MN Info:', mninfo);

        console.log('Balance:', balanceNrg, 'NRG');
        console.log('Balance:', balanceWei, 'Wei');

    }
    catch (err) {
        console.error(err);
    }
};
 
// example Energi address:
const myAddress =  process.env.NRG_ADDR;
 
showBalance(myAddress);