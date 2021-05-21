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
proof_t = {'z': ZR, 't': GT, 'y': GT}
proof1_t = {'z1': ZR, 'z2': ZR, 't': GT, 'y': GT}
prf_t= {'H':G1, 't':G1, 'c':ZR, 'r':ZR}


class Merchant():
    def __init__(self):
        global Mer, groupObj
        groupObj = PairingGroup('BN254')
    #Nir = Nirvana(groupObj)
        self.PoK = PoK(groupObj)
        self.SSS = SecretShare(groupObj)
        Mer = ['Apple','Ebay','Tesco','Amazon','Tesla','Colruyt','BMW','hp','Albert','IKEA']

    #
    

    

    # poller = zmq.Poller()
    # poller.register(socket, zmq.POLLIN)
    # poller.register(socket_pull, zmq.POLLIN)


    def request_pp(self):
        self.context = zmq.Context()
        print("Connecting to NirvanaTTP, requesting parameters...")
        socket_pull = self.context.socket(zmq.PULL)
        socket_pull.connect("tcp://10.0.2.15:5556")
        mpk = socket_pull.recv()
        mpk = mpk.decode('utf-8')
        mpk = bytesToObject(mpk, groupObj)
        #print(mpk)
        socket_pull.close()
        return mpk

    def request_pk(self):
        self.context = zmq.Context()
        print("Connecting to NirvanaTTP, requesting public key...")
        socket = self.context.socket(zmq.REQ)
        socket.connect("tcp://10.0.2.15:5557")
        print(f"Sending request for public key ...")
        socket.send_string("Apple")

        self.message_pk = socket.recv()
        #message = message.decode('utf-8')
        self.merchant_public_key = groupObj.deserialize(self.message_pk)
        print(f"Received public key [ {self.merchant_public_key} ]")
        socket.close()
    
    def request_proof(self):
        print("Connecting to customer, requesting proofs and ciphertext...")
        socket_receiveProof = self.context.socket(zmq.REQ)
        socket_receiveProof.connect("tcp://10.0.2.15:5550")
        self.merchant_public_key = groupObj.serialize(self.merchant_public_key)
        socket_receiveProof.send(self.merchant_public_key)
        #time.sleep(0.2)
        print("Received proof is ...")
        received_proof =  socket_receiveProof.recv()
        received_proof = bytesToObject(received_proof, groupObj)
        master_public_key = received_proof[0]
        print(type(master_public_key))
        payment_cipher_text = received_proof[1]
        randomization_stuff = received_proof[2]
        proof1_stuff = received_proof[3]
        proof2_stuff = received_proof[4]
        proof3_stuff = received_proof[5]
        proof4_stuff = received_proof[6]

        return master_public_key, randomization_stuff, payment_cipher_text, proof1_stuff, proof2_stuff, proof3_stuff, proof4_stuff, self.merchant_public_key




    @Input(mpk_t, Rand_t, ct_t, proof_t, proof_t, proof_t, proof1_t, G2, int, list, ZR)
    @Output(list)
    def Verification(self, mpk, Rand, ct, proof1, proof2, proof3, proof4, mer_pk, d, Ledger, time):
        LHS=1
        print("im here")
        for i in range(len(ct['R'])):
            LHS *= (mpk['e_gh'] * ct['R'][i] ** (-time)) 
        if pair(Rand['Sprime'], Rand['Rprime']) == proof1['y'] * mpk['e_Xh'] ** d and \
            pair(Rand['Tprime'],Rand['Rprime']) == pair(Rand['Sprime'],mpk['vk']) * mpk['e_gh']**d and \
                LHS==proof2['y'] and \
                    pair(mpk['g'],mpk['pp']) * (ct['C']**(-time)) == proof4['y'] and \
                    pair(mpk['g'],mer_pk) * (ct['C1'] ** (-time)) == proof3['y'] and \
                    PoK.verifier3(mpk['g'],proof1['y'],proof1['z'],proof1['t'],mpk['vk']) == 1 and \
                        PoK.verifier4(proof2['y'],proof2['z'],proof2['t'],ct['R']) == 1 and \
                            PoK.verifier3(proof3['y'],proof3['z'],proof3['t'],ct['C1'],mer_pk) == 1 and \
                                PoK.verifier2(ct['C'],mpk['e_gh'],proof4['y'],proof4['z1'],proof4['z2'],proof4['t'])==0 and \
                                ct['R'] not in Ledger:
                Ledger.append(ct['R'])
                return Ledger
        else:
            return Ledger

    @Input(mpk_t, ct_t, int, ct_t, int)
    @Output(GT)
    def Decryption(self, mpk, ct1, M1, ct2, M2): 
        Coeff = SSS.recoverCoefficients([group.init(ZR, M1+1),group.init(ZR, M2+1)])
        return ct2['C'] / ((ct1['C1']**Coeff[M1+1])*(ct2['C1']**Coeff[M2+1]))

groupObj = PairingGroup('BN254')    
time=groupObj.hash(objectToBytes(str(datetime.now()), groupObj),ZR)
m = Merchant()
#m.request_pp()
m.request_pk()
#c.request_pp()
#c.request_col()
m.Verification(m.request_proof(), 1, [], time)



    

    
