from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.toolbox.secretutil import SecretUtil
from charm.toolbox.ABEnc import Input, Output
from secretshare import SecretShare
from charm.core.engine.util import serializeDict,objectToBytes, bytesToObject
import random
import time
import zmq
#from NirvanaTTP import Nirvana
from datetime import datetime
from openpyxl import load_workbook
from openpyxl import Workbook
from PoK import PoK

mpk_t = { 'g':G1, 'h':G2, 'pp': G2, 'e_gh':GT, 'e_Xh':GT, 'vk':G2 , 'X': G1 }
msk_t = { 'sec':ZR, 'sgk':ZR }
pk_t = { 'pk':G2, 'Merlist':str }
sk_t = { 'shares': ZR }
Col_t = { 'PRFkey': ZR, 'key':G1, 'R':G2, 'S':G1, 'T':G1, 'W':G1 }
Rand_t = {'Rprime':G2, 'Sprime':G1, 'Tprime':G1, 'Wprime':G1}
ct_t = { 'C':GT, 'C1':GT, 'R':GT}
proof1_t = {'p1z': ZR, 'p1t': GT, 'p1y': GT}
proof4_t = {'p4z': ZR, 'p4t': GT, 'p4y': GT}
proof3_t = {'p3z': ZR, 'p3t': GT, 'p3y': GT}
proof2_t = {'p2z1': ZR, 'p2z2': ZR, 'p2t': GT, 'p2y': GT}
prf_t= {'H':G1, 't':G1, 'c':ZR, 'r':ZR}



class Customer():

    def __init__(self):
        global Mer, groupObj
        groupObj = PairingGroup('BN254')
    #Nir = Nirvana(groupObj)
        self.PoK = PoK(groupObj)
        self.SSS = SecretShare(groupObj)
        Mer = ['Apple','Ebay','Tesco','Amazon','Tesla','Colruyt','BMW','hp','Albert','IKEA'] 
        
    # @Input(mpk_t, Col_t, pk_t, ZR, int, int, ZR, GT)
    # @Output(ct_t,Rand_t,proof_t,proof_t,proof_t,proof1_t)
    # def Spending(self, mpk, Col, pk, time, d ,N, IDsk,ID):
    #     SAgg=1; TAgg=1; PRFkey=0; R=[]; X=[]; y2=1
    #     if len(Col['PRFkey']) >= d:
    #         for i in range(d):
    #             SAgg *= Col['S'][i]
    #             TAgg *= Col['T'][i]
    #             PRFkey += Col['PRFkey'][i]
    #             R.append(mpk['e_gh'] ** (1/(Col['PRFkey'][i]+time)))
    #             X.append(Col['PRFkey'][i])
    #             y2 *= R[i] ** X[i]
    #             A = pair(mpk['g'],mpk['vk']) ** PRFkey
    #         tprime = group.random(ZR)
    #         Rprime = Col['R'] ** (1/tprime)
    #         Sprime = SAgg ** tprime
    #         Tprime = (TAgg ** (tprime**2))* (Col['W']**(d*tprime*(1-tprime)))
    #         Wprime = Col['W'] ** (1/tprime)
    #         r = mpk['g'] ** (1/(PRFkey+time))
    #         C = ID * (pair(r, mpk['pp']))
    #         C1 = pair(r, pk['pk'][N])
    #         (proof1) = PoK2.prover(mpk['g'],A,PRFkey,mpk['vk']) #Proof of SPS
    #         (proof2) = PoK3.prover(y2,X,R) # Proof of Aggeragetd collatorals
    #         (proof3) = PoK2.prover(r,C1**PRFkey,PRFkey,pk['pk'][N]) #Proof of ciphertext C1
    #         (proof4) = PoK1.prover2(C,mpk['e_gh'],((C/ID)**PRFkey)*(mpk['e_gh']**(-time*IDsk)),PRFkey,(-time*IDsk)) #Proof of ciphertext C0
    #         Rand = { 'Rprime':Rprime, 'Sprime':Sprime, 'Tprime':Tprime, 'Wprime':Wprime }
    #         ct = { 'C': C, 'C1': C1, 'R':R }
    #         return (ct, Rand, proof1, proof2, proof3, proof4)
    #     else:
    #         return (print("You don't have enough money in your account"), None)


    

    # print("Connecting to NirvanaTTP, requesting collateral proof...")
    # socket = context.socket(zmq.REQ)
    # socket.connect("tcp://10.0.2.15:5551")
    # socket_pull = context.socket(zmq.PULL)
    # socket_pull.connect("tcp://10.0.2.15:5556")

    # poller = zmq.Poller()
    # poller.register(socket, zmq.POLLIN)
    # poller.register(socket_pull, zmq.POLLIN)



    #socks = dict(poller.poll())
    #if socket_pull in socks:
    @Output(mpk_t)
    def request_pp(self):
        self.context = zmq.Context()
        print("Connecting to NirvanaTTP, requesting parameters...")
        socket_pull = self.context.socket(zmq.PULL)
        socket_pull.connect("tcp://10.0.2.15:5556")
        mpk = socket_pull.recv()
        #mpk = mpk.decode('utf-8')
        mpk = bytesToObject(mpk, groupObj)
        #print(mpk)
        socket_pull.close()
        return mpk
    
    @Output(Col_t)
    def request_col(self): 
        print("Connecting to NirvanaTTP, requesting collateral proof...")
        socket = self.context.socket(zmq.REQ)
        socket.connect("tcp://10.0.2.15:5551")   
        for request in range(1):
            print(f"Sending request {request} ...")
            socket.send_string('2')

            message_col = socket.recv()
            #message_col = message_col.decode('utf-8')
            message_col = bytesToObject(message_col, groupObj)
            #print(f"Received collateral [ {message_col} ]")
            #message_col = {int(k):v for k in message_col.values()}
            print(message_col)
        socket.close()
        return message_col

    @Input(mpk_t, Col_t, int)
    def spend_col(self, mpk, Col, d):
        socket_receiveProofReq = self.context.socket(zmq.REP)
        socket_receiveProofReq.bind("tcp://10.0.2.15:5550")
        
        
        IDsk = groupObj.random(ZR); ID= mpk['e_gh']**IDsk 
        pk_message = socket_receiveProofReq.recv()
        pk_message = groupObj.deserialize(pk_message)
        time=groupObj.hash(objectToBytes(str(datetime.now()), groupObj),ZR)
        SAgg=1; TAgg=1; PRFkey=0; R=[]; X=[]; y2=1
        if len(Col['PRFkey']) >= d:
            for i in range(d):
                SAgg *= Col['S'][str(i)]
                TAgg *= Col['T'][str(i)]
                valPRF = Col['PRFkey'][str(i)]
                PRFkey += valPRF
                R.append(mpk['e_gh'] ** (1/valPRF+time))
                X.append(valPRF)
                y2 *= R[i] ** X[i]
                A = pair(mpk['g'],mpk['vk']) ** PRFkey
            tprime = groupObj.random(ZR)
            Rprime = Col['R'] ** (1/tprime)
            Sprime = SAgg ** tprime
            Tprime = (TAgg ** (tprime**2))* (Col['W']**(d*tprime*(1-tprime)))
            Wprime = Col['W'] ** (1/tprime)
            r = mpk['g'] ** (1/(PRFkey+time))
            C = ID * (pair(r, mpk['pp']))
            C1 = pair(r, pk_message)
            (proof1) = self.PoK.prover1(mpk['g'],A,PRFkey,mpk['vk']) #Proof of SPS
            (proof2) = self.PoK.prover4(y2,X,R) # Proof of Aggeragetd collatorals
            (proof3) = self.PoK.prover3(r,C1**PRFkey,PRFkey,pk_message) #Proof of ciphertext C1
            (proof4) = self.PoK.prover2(C,mpk['e_gh'],((C/ID)**PRFkey)*(mpk['e_gh']**(-time*IDsk)),PRFkey,(-time*IDsk)) #Proof of ciphertext C0
            Rand = { 'Rprime':Rprime, 'Sprime':Sprime, 'Tprime':Tprime, 'Wprime':Wprime }
            ct = { 'C': C, 'C1': C1, 'R':R }
            spend_proofs = (mpk, Rand, ct, proof1, proof2, proof3, proof4)
            spend_proofs = objectToBytes(spend_proofs, groupObj)
            socket_receiveProofReq.send(spend_proofs)
        #(ct1, Rand1,proof1,proof2,proof3,proof4) = Nir.Spending(mpk, Col, pk_message, time, d, N, IDsk, ID)
        # ct1= serializeDict(ct, groupObj)
        # Rand1= objectToBytes(Rand, groupObj)
        # proof1= objectToBytes(proof1, groupObj)
        # proof2= objectToBytes(proof2, groupObj)
        # proof3= objectToBytes(proof3, groupObj)
        # proof4= objectToBytes(proof4, groupObj)
        # #print(proof4)
        # socket_receiveProofReq.send_multipart(ct1, zmq.SNDMORE)
        # socket_receiveProofReq.send_multipart(Rand1, zmq.SNDMORE)
        # socket_receiveProofReq.send_multipart(proof1, zmq.SNDMORE)
        # socket_receiveProofReq.send_multipart(proof2, zmq.SNDMORE)
        # socket_receiveProofReq.send_multipart(proof3, zmq.SNDMORE)
        # socket_receiveProofReq.send_multipart(proof4)

        socket_receiveProofReq.close()
    # print("Connecting to NirvanaTTP")
    # socket = context.socket(zmq.REQ)
    # socket.connect("tcp://10.0.2.15:5555")
    # print(f"Current libzmq version is {zmq.zmq_version()}")
    # for request in range(5):
    #     print(f"Sending request {request} ...")
    #     socket.send_string("Hello")

    #     message = socket.recv()
    #     print(f"Received reply {request} [ {message.decode('utf-8')} ]")
c = Customer()
#c.request_pp()
#c.request_col()
c.spend_col(c.request_pp(), c.request_col(), 1)