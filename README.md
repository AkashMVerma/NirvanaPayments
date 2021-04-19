# NirvanaPayments

Nirvana.sol = Smart contract which enables customers to deposit their collateral and make failsafe payments to merchants. Each customer can make mutliple payments to any merchant. 

NirvanaPaymentChannel.sol = Customer's deposit a collateral. This collateral can be used to send encrypted payment promises to merchants which can only be decrypted if the customer double spends. We still need to add the conditional decryption part. For now all payment promises are instantly available to the merchant which can be used for claimPayment() function. 

Nirvana.c = C code for testing the functionality of trusted Nirvana. Used for benchmarking its performance. 

NirvanaPayments.js = Script used to invoke and execute NirvanaPaymentChannel.sol
