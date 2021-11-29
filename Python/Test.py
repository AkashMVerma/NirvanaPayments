from Nirvana import Nirvana   
from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.toolbox.secretutil import SecretUtil
from BLS import BLS01
#from charm.toolbox.ABEnc import Input, Output
from secretshare import SecretShare
from charm.core.engine.util import serializeDict,objectToBytes
from openpyxl import load_workbook
from openpyxl import Workbook
import math
from TSPS import TSPS
import random
from datetime import datetime

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
TSPS=TSPS(groupObj)
BLS01=BLS01(groupObj)
Mer = ['Apple'] * 10
Cus = ['Alice'] * 20
n=10; k=math.floor(n/2)
Ledger=[]
time=groupObj.hash(objectToBytes(str(datetime.now()), groupObj),ZR)

(mpk) = Nir.PGen()
(Sgk_a,Vk_a,Pk_a) = Nir.AuKeygen(mpk, k,n)
(Vk_b,Sk_b) = Nir.MKeygen(mpk,len(Mer))
(Pk_b,cert_b) = Nir.MRegister(mpk,Sgk_a,Vk_b,len(Mer),k)
(Sk_c,Pk_c) = Nir.CuKeyGen(mpk,len(Cus))
(cert_c) = Nir.CuRegister(mpk,Sgk_a,Pk_c,len(Cus),k)
(key, N, kprime,certprime) = Nir.CuCreate(mpk,cert_c[10])
cert_j = Nir.AuCreate(mpk,Sgk_a,kprime,k)
ID = mpk['e_gh'] ** Sk_c[10]
(pi,inp,R) = Nir.Spending(mpk, key, Pk_b[8], time,ID, Sk_c[10],cert_j)
L1=pair(mpk['g'],mpk['pp']) 
L2=pair(mpk['g'],Pk_b[8])
out = Nir.Verification(mpk, Pk_a, N, pi, inp, R, Ledger, time,L1,L2, Pk_b[8])
print(out)
#Nir.Decryption(  mpk, ct1, M1, ct2, M2)

'''
def run_round_trip(n,d,M):
    result=[n,d,M]
    # setup
    
    setup_time = 0
    for i in range(1):
        start_bench(groupObj)
        (mpk) = Nir.PGen(math.floor(n/2),n)
        setup_time += end_bench(groupObj)
    setup_time = setup_time * 10
    result.append(setup_time)
    public_parameters_size = sum([len(x) for x in serializeDict(mpk, groupObj).values()]) 
    result.append(public_parameters_size)
    # Key Gen
    Merchants = random.sample(Mer, M)
    Key_Gen_time=0
    for i in range(1):
        start_bench(groupObj)
        (Sgk_a,Vk_a,Pk_a) = Nir.AuKeygen(mpk, math.floor(n/2),n)
        Key_Gen_time += end_bench(groupObj)
    Key_Gen_time = Key_Gen_time * 10
    public_key_size = sum([len(x) for x in serializeDict(mpk, groupObj).values()]) 
    #secret_key_size = sum([len(x) for x in serializeDict(msk, groupObj).values()]) 
    #secret_key_size = secret_key_size /10
    public_key_size = public_key_size /10
    result.append(Key_Gen_time)
    result.append(public_key_size)
    #result.append(secret_key_size)

    # Registeration
    
    Registeration_time=0
    for i in range(1):
        start_bench(groupObj)
        (Col) = Nir.Registeration(mpk, Sgk_a, n)
        Registeration_time += end_bench(groupObj)
    Registeration_time = Registeration_time * 10
    Collateral_size = sum([len(x) for x in serializeDict(Col, groupObj).values()]) 
    Collateral_size = Collateral_size /10
    result.append(Registeration_time)
    result.append(Collateral_size)

    # Spending
    
    #N = pk['Merlist'].index('Apple')
    Spending_time = 0; time=groupObj.hash(objectToBytes(str(datetime.now()), group),ZR)
    for i in range(1):
        start_bench(groupObj)
        (ct1, Rand1,proof1,proof2) = Nir.Spending(mpk, Col, pk, time, d, 10)
        Spending_time += end_bench(groupObj)
    Spending_time = Spending_time * 10
    result.append(Spending_time)
    Ciphertext_size = sum([len(x) for x in serializeDict(ct1, groupObj).values()]) + sum([len(x) for x in serializeDict(Rand1, groupObj).values()]) 
    result.append(Ciphertext_size)
    (ct2, Rand2,p1,p2) = Nir.Spending(mpk, Col, pk, time, d, 11)

    # Verification 
    Verification_time = 0
    for i in range(1):
        start_bench(groupObj)
        Ledger=[]
        out = Nir.Verification(mpk,Rand1,ct1,proof1,proof2,d,Ledger,time)
        print(out)
        Verification_time += end_bench(groupObj)
    Verification_time = Verification_time * 10
    result.append(Verification_time) 
    #(out2)= Nir.Verification(mpk,ct2,Rand2)


    # Decryption
    Decryption_time = 0
    for i in range(1):
        start_bench(groupObj)
        (out)= Nir.Decryption(mpk, ct1, 1, ct2, 2)
        Decryption_time += end_bench(groupObj)
    Decryption_time = Decryption_time * 10
    result.append(Decryption_time)

    return result

book=Workbook()
data=book.active
title=["n","d","M","setup_time","public_parameters_size", "Key_Gen_time","public_key_size","secret_key_size","Registeration_time","Collateral_size","Spending_time","Ciphertext_size","Verification_time","Decryption_time"]
data.append(title)
for n in range(2,3):
    data.append(run_round_trip(n,n,50*n))
    print(n)
book.save("Result1.xlsx")

'''