from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.toolbox.secretutil import SecretUtil
from charm.toolbox.ABEnc import Input, Output
from secretshare import SecretShare
from charm.core.engine.util import serializeDict,objectToBytes, bytesToObject, deserializeDict
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

    @Output(mpk_t)
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

    @Output(G2)
    def request_pk(self):
        self.context = zmq.Context()
        print("Connecting to NirvanaTTP, requesting public key...")
        socket = self.context.socket(zmq.REQ)
        socket.connect("tcp://10.0.2.15:5557")
        print(f"Sending request for public key ...")
        socket.send_string("Apple")

        message_pk = socket.recv()
        #message = message.decode('utf-8')
        merchant_public_key = bytesToObject(message_pk, groupObj)
        print(f"Received public key [ {merchant_public_key} ]")
        socket.close()
        return merchant_public_key

    @Input(G2)
    @Output(mpk_t, Rand_t, ct_t, proof1_t, proof4_t, proof3_t, proof2_t, ZR)
    def request_proof(self, merchant_public_key):
        print("Connecting to customer, requesting proofs and ciphertext...")
        socket_receiveProof = self.context.socket(zmq.REQ)
        socket_receiveProof.connect("tcp://10.0.2.15:5550")
        merchant_public_key = groupObj.serialize(merchant_public_key)
        socket_receiveProof.send(merchant_public_key)
        #time.sleep(0.2)
        print("Received proof is ...")
        received_proof =  socket_receiveProof.recv()
        received_proof = bytesToObject(received_proof, groupObj)
        #received_proof = bytesToObject(received_proof, groupObj)
        #print(received_proof)
        return received_proof
        # LHS=1
        # print(range(len(ct['R'])))
        # for i in range(len(ct['R'])):
        #     print(ct['R'][i])
        #     LHS *= (mpk['e_gh'] * ct['R'][i] ** (-time)) 
        # if pair(Rand['Sprime'], Rand['Rprime']) == proof1['p1y'] * mpk['e_Xh'] ** d and \
        #     pair(Rand['Tprime'],Rand['Rprime']) == pair(Rand['Sprime'],mpk['vk']) * mpk['e_gh']**d and \
        #         LHS==proof2['p4y'] and \
        #             pair(mpk['g'],mpk['pp']) * (ct['C']**(-time)) == proof4['p2y'] and \
        #             pair(mpk['g'],pk['pk'][N]) * (ct['C1'] ** (-time)) == proof3['p3y'] and \
        #             PoK.verifier3(mpk['g'],proof1['p1y'],proof1['p1z'],proof1['p1t'],mpk['vk']) == 1 and \
        #                 PoK.verifier5(proof2['p4y'],proof2['p4z'],proof2['p4t'],ct['R']) == 1 and \
        #                     PoK.verifier4(proof3['p3y'],proof3['p3z'],proof3['p3t'],ct['C1'],pk['pk'][N]) == 1 and \
        #                         PoK.verifier2(ct['C'],mpk['e_gh'],proof4['p2y'],proof4['p2z1'],proof4['p2z2'],proof4['p2t'])==0 and \
        #                         ct['R'] not in Ledger:
        #         Ledger.append(ct['R'])
        #         print("works")
        #         return Ledger
        # else:
        #     print("doesnt work")
        #     return Ledger

        




    @Input(mpk_t, Rand_t, ct_t, proof1_t, proof4_t, proof3_t, proof2_t, G2, int, list, ZR)
    @Output(list)
    def Verification(self, mpk, Rand, ct, proof1, proof2, proof3, proof4, mer_pk, d, Ledger, time):
        LHS=1
        print(mpk)
        for i in range(len(ct['R'])):
            LHS *= (mpk['e_gh'] * ct['R'][i] ** (-time)) 
        if pair(Rand['Sprime'], Rand['Rprime']) == proof1['p1y'] * mpk['e_Xh'] ** d and \
            pair(Rand['Tprime'],Rand['Rprime']) == pair(Rand['Sprime'],mpk['vk']) * mpk['e_gh']**d and \
                LHS!=proof2['p4y'] and \
                    pair(mpk['g'],mpk['pp']) * (ct['C']**(-time)) == proof4['p2y'] and \
                    pair(mpk['g'],mer_pk) * (ct['C1'] ** (-time)) == proof3['p3y'] and \
                    PoK.verifier3(mpk['g'],proof1['p1y'],proof1['p1z'],proof1['p1t'],mpk['vk']) == 1 and \
                        PoK.verifier5(proof2['p4y'],proof2['p4z'],proof2['p4t'],ct['R']) == 1 and \
                            PoK.verifier4(proof3['p3y'],proof3['p3z'],proof3['p3t'],ct['C1'],mer_pk) == 1 and \
                                PoK.verifier2(ct['C'],mpk['e_gh'],proof4['p2y'],proof4['p2z1'],proof4['p2z2'],proof4['p2t'])==0 and \
                                ct['R'] not in Ledger:
                Ledger.append(ct['R'])
                print("passed")
                return Ledger
        else:
            print("not passed")
            return Ledger


    @Input(mpk_t, ct_t, int, ct_t, int)
    @Output(GT)
    def Decryption(self, mpk, ct1, M1, ct2, M2): 
        Coeff = SSS.recoverCoefficients([group.init(ZR, M1+1),group.init(ZR, M2+1)])
        return ct2['C'] / ((ct1['C1']**Coeff[M1+1])*(ct2['C1']**Coeff[M2+1]))

# groupObj = PairingGroup('BN254')    

m = Merchant()
# #m.request_pp()
mer_pk = m.request_pk()
# #c.request_pp()
# #c.request_col()
spend_proof = m.request_proof(mer_pk)
# #print(output_proof)
#
#@Input(mpk_t, Rand_t, ct_t, proof1_t, proof4_t, proof3_t, proof2_t, G2, int, list, ZR)
d=1
Ledger = []
mpkst = spend_proof[0]
randomstr = spend_proof[1]
ct1st = spend_proof[2]
proof1st = spend_proof[3]
proof2st = spend_proof[4]
proof3st = spend_proof[5]
proof4st = spend_proof[6]
timest = spend_proof[7]
out = m.Verification(mpkst, randomstr, ct1st, proof1st, proof2st, proof3st, proof4st, mer_pk, d, Ledger, timest)



    

    
