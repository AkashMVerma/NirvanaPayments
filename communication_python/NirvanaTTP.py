from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.toolbox.secretutil import SecretUtil
#from charm.toolbox.ABEnc import Input, Output
from secretshare import SecretShare
from charm.core.engine.util import bytesToObject, serializeDict,objectToBytes
import random
import time
import zmq
import json
from datetime import datetime
from openpyxl import load_workbook
from openpyxl import Workbook
from PoK import PoK
from TSPS import TSPS
from BLS import BLS01


context = zmq.Context()
socket_clientReg = context.socket(zmq.REP)
socket_clientReg.bind("tcp://*:5551") #customer connection
socket_clientSig = context.socket(zmq.REP)
socket_clientSig.bind("tcp://*:5558") #customer connection
socket_merchant = context.socket(zmq.REP)
socket_merchant.bind("tcp://*:5557") #merchant connection
socket_publish = context.socket(zmq.PUSH)
socket_publish.bind("tcp://*:5556") #publishing mpk

'''
mpk_t = { 'g':G1, 'h':G2, 'pp': G2, 'e_gh':GT, 'e_Xh':GT, 'vk':G2 , 'X': G1 }
msk_t = { 'sec':ZR, 'sgk':ZR }
pk_t = { 'pk':G2, 'Merlist':str }
sk_t = { 'shares': ZR }
Col_t = { 'PRFkey': ZR, 'key':G1, 'R':G2, 'S':G1, 'T':G1, 'W':G1 }
Rand_t = {'Rprime':G2, 'Sprime':G1, 'Tprime':G1, 'Wprime':G1}
ct_t = { 'C':GT, 'C1':GT, 'R':GT}
proof_t = {'z': ZR, 't': GT, 'y': GT}
proof1_t = {'z1': ZR, 'z2': ZR, 't': GT, 'y': GT}
prf_t= {'H':G1, 't':G1, 'c':ZR, 'r':ZR}
'''

class Nirvana():
    def __init__(self, groupObj):
        global util, group
        util = SecretUtil(groupObj)
        group = groupObj
    
      
    def Setup(self,k,n):
        (msk, pk) = TSPS.setup()
        e_gh = pair(pk['g'],pk['h'])
        mpk = {'g':pk['g'], 'h':pk['h'], 'X':pk['X'], 'Y':pk['Y'], 'e_gh':e_gh}
        return (mpk, msk)
        return (mpk, msk)

    
    def AuKeygen(self, mpk, msk,k,n):
        (sgk,vk) = TSPS.kgen(msk,mpk,k,n)
        AL={'sgk':sgk,'vk':vk}
        return AL

    def MKeygen(self,mpk,M):
        Vkm={};Skm={}
        for i in range(len(M)):
            (vkm,skm)=BLS01.keygen(mpk['g'])
            Vkm[i]=vkm; Skm[i]=skm
        ML={'vkm':Vkm, 'MerList':M}    
        return ML

    def CuRegister(mpk,sgk,pk,k):
        cert={}
        sigma1=TSPS.par_sign1(mpk,pk,k)
        sigma=TSPS.par_sign2(sigma1,sgk,k)
        sigmaR=TSPS.reconst(sigma,k)
        cert=sigmaR
        return cert

    def AuCreate(mpk,sgk,kprime,co,k):
        cert={}
        for i in range(co):
            sigma1=TSPS.par_sign1(mpk,kprime,k)
            sigma=TSPS.par_sign2(sigma1,sgk,k)
            sigmaR=TSPS.reconst(sigma,k)
            cert[i]=sigmaR
        return cert

    
    
    '''
    def MRegister(mpk,sgk,vkm,M,k):
        cert={}
        for i in range(len(M)):
            sigma1=TSPS.par_sign1(mpk,vkm,k)
            sigma=TSPS.par_sign2(sigma1,sgk,k)
            sigmaR=TSPS.reconst(sigma,k)
            cert[i]=sigmaR
        return cert
    '''

    def Registeration(self, mpk, msk, n):
        PRFkey={}; key={}; S={}; T={}; t=group.random(ZR)
        for i in range(n):
            PRFkey[i] = group.random(ZR)
            key[i]= mpk['g'] ** PRFkey[i]
            S[i] = (key[i] ** (msk['sgk']/t)) * (mpk['X']**(1/t))
            T[i] = (S[i] ** (msk['sgk']/t)) * (mpk['g']**(1/t))
        R = mpk['h']**t
        W = mpk['g']**(1/t)
        return { 'PRFkey': PRFkey, 'key': key, 'R':R, 'S':S, 'T':T, 'W':W }

groupObj = PairingGroup('BN254')
Nir = Nirvana(groupObj)
PoK = PoK(groupObj)
SSS = SecretShare(groupObj)
Mer = ['Apple','Ebay','Tesco','Amazon','Tesla','Colruyt','BMW','hp','Albert','IKEA']

#setup
(mpk, msk) = Nir.Setup()
keep_sending = True
# while keep_sending:
#     message_mpk = objectToBytes(mpk, group)
#     socket_publish.send(message_mpk)
#     time.sleep(10)
#     keep_sending = False
(pk,sk) = Nir.Keygen(mpk, msk, Mer)
(sgk,vk) = Nir.AuKeygen(mpk, msk, 1,1)

#setting up poller
poller = zmq.Poller()
poller.register(socket_clientReg, zmq.REQ)
poller.register(socket_clientSig, zmq.REQ)
poller.register(socket_merchant, zmq.REQ)

#receiving requests
keep_receiving = True
while keep_receiving:
    socks = dict(poller.poll())
    if(socket_clientReg) in socks:
        message_clientReg = socket_clientReg.recv(zmq.DONTWAIT)
        message_clientReg = bytesToObject(message_clientReg,groupObj)
        print(f"Received registration request for Customer with Public Key: {message_clientReg}")
        cert = (mpk, Nir.CuRegister(mpk,sgk, message_clientReg,1))
        approved_registration = objectToBytes(cert,groupObj)
        socket_clientReg.send(approved_registration)
        print(f"Sent approval to client {message_clientReg}..")
        socket_clientReg.close()

    if socket_clientSig in socks:
        #Registration
        message_client = socket_clientSig.recv(zmq.DONTWAIT)
        message_client = objectToBytes(message_client,groupObj)
        k_prime = message_client[0]
        num_col = message_client[1]
        print(f"Received request from customer for collateral signature..")
        data_to_send = (Nir.AuCreate(mpk,sgk,k_prime, num_col, 1))
        #print(Col)
        collateral_proofs = objectToBytes(data_to_send, groupObj)
        socket_clientSig.send(collateral_proofs)
        print("Sent collateral proof..")
        socket_clientSig.close()
        
    if socket_merchant in socks:
        #keygen
        message_merchant = socket_merchant.recv(zmq.DONTWAIT)
        print(f"Received request: {message_merchant}")
        message_merchant = message_merchant.decode('utf-8')
        N = pk['Merlist'].index(message_merchant)
        public_key = objectToBytes(pk['pk'][N], group)
        socket_merchant.send(public_key)
        print("Sent public key information to merchant..")
        socket_merchant.close()

        keep_receiving = False        
        
