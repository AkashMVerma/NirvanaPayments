from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.toolbox.secretutil import SecretUtil
from charm.toolbox.ABEnc import Input, Output
from secretshare import SecretShare
from charm.core.engine.util import objectToBytes
import random
from openpyxl import load_workbook
from openpyxl import Workbook


def start_bench(group):
    group.InitBenchmark()
    group.StartBenchmark(["RealTime"])

def end_bench(group):
    group.EndBenchmark()
    benchmarks = group.GetGeneralBenchmarks()
    real_time = benchmarks['RealTime']
    return real_time

groupObj = PairingGroup('BN254')
Nir = Nirvana(groupObj)
SSS = SecretShare(groupObj)

def run_round_trip(n,d,M):
    result=[n,d,M]
    # setup
    start_bench(groupObj)
    (mpk, msk) = Nir.Setup()
    setup_time = end_bench(groupObj)
    result.append(setup_time)
    public_parameters_size = len(objectToBytes(mpk, groupObj))
    result.append(public_parameters_size)
    # Key Gen
    start_bench(groupObj)
    Mer = ['Apple', 'Tesco', 'Tesla', 'Amazon', 'Bol', 'Ebay', 'Colruyt', 'Delhaize', 'Albert', 'IKEA', 'Apple', 'Tesco', 'Tesla', 'Amazon', 'Bol', 'Ebay', 'Colruyt', 'Delhaize', 'Albert', 'IKEA', 'Apple', 'Tesco', 'Tesla', 'Amazon', 'Bol', 'Ebay', 'Colruyt', 'Delhaize', 'Albert', 'IKEA', 'Apple', 'Tesco', 'Tesla', 'Amazon', 'Bol', 'Ebay', 'Colruyt', 'Delhaize', 'Albert', 'IKEA', 'Apple', 'Tesco', 'Tesla', 'Amazon', 'Bol', 'Ebay', 'Colruyt', 'Delhaize', 'Albert', 'IKEA', 'Apple', 'Tesco', 'Tesla', 'Amazon', 'Bol', 'Ebay', 'Colruyt', 'Delhaize', 'Albert', 'IKEA', 'Apple', 'Tesco', 'Tesla', 'Amazon', 'Bol', 'Ebay', 'Colruyt', 'Delhaize', 'Albert', 'IKEA', 'Apple', 'Tesco', 'Tesla', 'Amazon', 'Bol', 'Ebay', 'Colruyt', 'Delhaize', 'Albert', 'IKEA','Apple', 'Tesco', 'Tesla', 'Amazon', 'Bol', 'Ebay', 'Colruyt', 'Delhaize', 'Albert', 'IKEA','Apple', 'Tesco', 'Tesla', 'Amazon', 'Bol', 'Ebay', 'Colruyt', 'Delhaize', 'Albert', 'IKEA','Apple', 'Tesco', 'Tesla', 'Amazon', 'Bol', 'Ebay', 'Colruyt', 'Delhaize', 'Albert', 'IKEA','Apple', 'Tesco', 'Tesla', 'Amazon', 'Bol', 'Ebay', 'Colruyt', 'Delhaize', 'Albert', 'IKEA','Apple', 'Tesco', 'Tesla', 'Amazon', 'Bol', 'Ebay', 'Colruyt', 'Delhaize', 'Albert', 'IKEA']
    Merchants=random.sample(Mer, M)
    print(Merchants)
    (pk,sk) = Nir.Keygen(mpk, msk, Merchants)
    Key_Gen_time = end_bench(groupObj)
    result.append(Key_Gen_time)

    # Registeration
    start_bench(groupObj)
    (Col) = Nir.Registeration(mpk, msk, n)
    Registeration_time = end_bench(groupObj)
    Collateral_size = len(objectToBytes(Col, groupObj))
    result.append(Registeration_time)
    result.append(Collateral_size)
    # Spending
    start_bench(groupObj)
    #N = pk['Merlist'].index('Apple')
    (ct1, Rand1) = Nir.Spending(mpk, Col, pk, 1235, d, 2)
    Spending_time = end_bench(groupObj)
    result.append(Spending_time)
    Ciphertext_size = len(objectToBytes(ct1, groupObj))
    result.append(Ciphertext_size)
    (ct2, Rand2) = Nir.Spending(mpk, Col, pk, 1235, d, 3)

    # Verification 
    start_bench(groupObj)
    (out1)= Nir.Verification(mpk,ct1,Rand1)
    Verification_time = end_bench(groupObj)
    result.append(Verification_time)
    #(out2)= Nir.Verification(mpk,ct2,Rand2)
    #print("\nIs the Second Merchant accepted?", out2)

    # Decryption
    start_bench(groupObj)
    (out)= Nir.Decryption(mpk, ct1, 2, ct2, 3)
    Decryption_time = end_bench(groupObj)
    result.append(Decryption_time)

    return result

book=Workbook()
data=book.active
title=["n","d","M","setup_time","public_parameters_size", "Key_Gen_time","Registeration_time","Collateral_size","Spending_time","Ciphertext_size","Verification_time","Decryption_time"]
data.append(title)
for n in range(2,100,2):
    data.append(run_round_trip(n,n,n+2))
book.save("Result.xlsx")
