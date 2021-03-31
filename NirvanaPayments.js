const EthCrypto = require('eth-crypto');
const ethabi = require("ethereumjs-abi");
const nirvanaIdentity = EthCrypto.createIdentity();
const merchantIdentity1 = EthCrypto.createIdentity();
const merchantIdentity2 = EthCrypto.createIdentity();
const customerIdentity = EthCrypto.createIdentity();
const Web3 = require('web3');
const paymentToBeSent = 500000000000000;
var web3 = new Web3('http://localhost:8545');
const ganache = require('ganache-core');
const eventEmitter = require('events');
//var pickUpLocation = "10.32.56.97";
//var dropOffLocation = "10.32.56.97";
//var carPlateNumber = "DL9C8R2618";
//var typeOfCar = "Sedan";



const ganacheProvider = ganache.provider({
    accounts: [
        // we preset the balance of our ownerIdentity to 100 ether
        {
            secretKey: merchantIdentity1.privateKey,
            balance: web3.utils.toWei('100', 'ether')
        },
        {
            secretKey: merchantIdentity2.privateKey,
            balance: web3.utils.toWei('100', 'ether')
        },
        // we also give some wei to the customerIdentity
        // so it can send transaction to the chain
        {
            secretKey: customerIdentity.privateKey,
            balance: web3.utils.toWei('100', 'ether')
        },
        {
            secretKey: nirvanaIdentity.privateKey,
            balance: web3.utils.toWei('100', 'ether')
        }
    ]
});

// set ganache to web3 as provider
web3.setProvider(ganacheProvider);


const path = require('path');
const fs = require('fs');
const solc = require('solc');
const EventEmitter = require('events');
const myEmmitter = new EventEmitter();
myEmmitter.removeAllListeners("uncaughtException");
myEmmitter.removeAllListeners("caughtException");
const inboxPath = path.resolve(__dirname, 'contracts', 'NirvanaPaymentChannel.sol');
const source = fs.readFileSync(inboxPath, 'utf8');

//module.exports = solc.compile(source,1).contracts[':NirvanaPaymentChannel'];
const input = {
    language: 'Solidity',
    sources: {
        'NirvanaPaymentChannel.sol' : {
            content: source
        },
    },
    settings: {
        outputSelection: {
            '*': {
                '*': [ '*' ]
            },
        },
    },
};


const compiled = JSON.parse(solc.compile(JSON.stringify(input)));

//module.exports = compiled.contracts["NirvanaPaymentChannel.sol"].Inbox;

const interface = compiled.contracts["NirvanaPaymentChannel.sol"].NirvanaPaymentChannel.abi;
const bytecode = compiled.contracts["NirvanaPaymentChannel.sol"].NirvanaPaymentChannel.evm.bytecode.object;
const createCode = EthCrypto.txDataByCompiled(compiled.contracts["NirvanaPaymentChannel.sol"].NirvanaPaymentChannel.abi, compiled.contracts["NirvanaPaymentChannel.sol"].NirvanaPaymentChannel.evm.bytecode.object, []);
//async function f2(){
//let abi = await new web3.eth.Contract(interface);
//}
//f2();
const customerPublicKey = customerIdentity.publicKey;
const customerPrivateKey = customerIdentity.privateKey;

//const merchantPublicKey = merchantIdentity.publicKey;
//const merchantPrivateKey = merchantIdentity.privateKey;
web3.eth.defaultAccount = customerIdentity.address;


//The deploy transaction, value is set to 5 ether so as to deploy the contract successfully.
const deployTx = {
    from:nirvanaIdentity.address,
    nonce:0,
    gasLimit:5000000,
    gasPrice:500000000,
    value: parseInt(web3.utils.toWei('0','ether')),
    data:createCode
};

//The owner signs the transaction to prove his identity. This signature is also checked on the blockchain.
const serializedTx = EthCrypto.signTransaction(deployTx, nirvanaIdentity.privateKey);


async function f1(){ 
    let receipt = await web3.eth.sendSignedTransaction(serializedTx);
    const contractAddress = receipt.contractAddress;
    const contractInstance = new web3.eth.Contract(interface, contractAddress);

    const customerRegistration = contractInstance.methods.registerCustomer().encodeABI();
    const registrationTx = {
        from:customerIdentity.address,
        to:contractAddress,
        nonce:0,
        gasLimit:5000000,
        gasPrice:500000000,
        data:customerRegistration,
        value:parseInt(web3.utils.toWei('5','ether'))
    }

    const serializedRegistrationTx = EthCrypto.signTransaction(registrationTx, customerPrivateKey);
    const receiptRequired = await web3.eth.sendSignedTransaction(serializedRegistrationTx); 


    const addingMerchants = contractInstance.methods.add_merchants([merchantIdentity1.address, merchantIdentity2.address]).encodeABI();
    const nirvanaAddMerchants = {
        from:nirvanaIdentity.address,
        to:contractAddress,
        nonce:1,
        gasLimit:5000000,
        gasPrice:500000000,
        data:addingMerchants,
    }

    const serializedAddingMerchantsTx = EthCrypto.signTransaction(nirvanaAddMerchants, nirvanaIdentity.privateKey);
    const receiptRequired2 = await web3.eth.sendSignedTransaction(serializedAddingMerchantsTx); 
    //const owner = await contractInstance.methods.carOwner().call();
    

    
    //function signPayment(contractAddress, callback) {
        //var hash = "0x" + ethabi.soliditySHA3(
        //    ["uint256", "address"],
       //     [parseInt(web3.utils.toWei('1','ether')), contractAddress]
       // ).toString("hex");
    
   //     web3.eth.personal.sign("0x"+ "Hello World", web3.eth.defaultAccount, function(err,signature){console.log(err)});
   // }

   // signPayment(contractAddress);

   const paymentMessage = EthCrypto.hash.keccak256([
    {
        type: 'address',
        value: contractAddress
    }, {
        type: 'uint256',
        value: paymentToBeSent
    }
]);

const signedPayment = EthCrypto.sign(customerIdentity.privateKey, paymentMessage);
/*
function toUTF8Array(str) {
    let utf8 = [];
    for (let i = 0; i < str.length; i++) {
        let charcode = str.charCodeAt(i);
        if (charcode < 0x80) utf8.push(charcode);
        else if (charcode < 0x800) {
            utf8.push(0xc0 | (charcode >> 6),
                      0x80 | (charcode & 0x3f));
        }
        else if (charcode < 0xd800 || charcode >= 0xe000) {
            utf8.push(0xe0 | (charcode >> 12),
                      0x80 | ((charcode>>6) & 0x3f),
                      0x80 | (charcode & 0x3f));
        }
        // surrogate pair
        else {
            i++;
            // UTF-16 encodes 0x10000-0x10FFFF by
            // subtracting 0x10000 and splitting the
            // 20 bits of 0x0-0xFFFFF into two halves
            charcode = 0x10000 + (((charcode & 0x3ff)<<10)
                      | (str.charCodeAt(i) & 0x3ff));
            utf8.push(0xf0 | (charcode >>18),
                      0x80 | ((charcode>>12) & 0x3f),
                      0x80 | ((charcode>>6) & 0x3f),
                      0x80 | (charcode & 0x3f));
        }
    }
    return utf8;
}
*/
//const signatureBytes = toUTF8Array(signedPayment);
const vrsSignedPayment = EthCrypto.vrs.fromString(signedPayment);
console.log(vrsSignedPayment);

const claimingPayment = contractInstance.methods.claim_payment(paymentToBeSent, vrsSignedPayment.v, vrsSignedPayment.r, vrsSignedPayment.s, customerIdentity.address).encodeABI();
const claimingPaymentTx = {
    from:merchantIdentity1.address,
    to:contractAddress,
    nonce:0,
    gasLimit:5000000,
    gasPrice:500000000,
    data:claimingPayment,
}
const serializedClaimingPaymentTx = EthCrypto.signTransaction(claimingPaymentTx, merchantIdentity1.privateKey);
const receiptRequired3 = await web3.eth.sendSignedTransaction(serializedClaimingPaymentTx); 

const customerInformation = await contractInstance.methods.customers(customerIdentity.address).call();
console.log(customerInformation);


const merchantInformation = await contractInstance.methods.merchants(merchantIdentity2.address).call();
console.log(merchantInformation);
web3.eth.getBalance(merchantIdentity1.address).then(console.log);
    //const signedDetails = EthCrypto.sign(ownerIdentity.privateKey, detailHash);

    //const signature = EthCrypto.sign(ownerIdentity.privateKey, signHash);

    //const vrs = EthCrypto.vrs.fromString(signature);

    //const vrsDetails = EthCrypto.vrs.fromString(signedDetails);

    //transaction for setting the required days
    //const requiredDays = contractInstance.methods.setRequiredDays(2).encodeABI();
    //const requiredTx = {
    //    from:customerIdentity.address,
    //    to:contractAddress,
    //    nonce:0,
    //    gasLimit:5000000,
    //    gasPrice:500000000,
     //   data: requiredDays,
    //}

    //const serializedRequiredTx = EthCrypto.signTransaction(requiredTx, customerIdentity.privateKey);

    //const receiptRequired = await web3.eth.sendSignedTransaction(serializedRequiredTx);


    //transaction for sending the encrypted details to the blockchain
    
    //console.dir(messa);

    //Transaction to call rentCar() function. Requires a value of 5 ether to be executed
   

}
f1();