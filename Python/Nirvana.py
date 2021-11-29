from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.toolbox.secretutil import SecretUtil
#from charm.toolbox.ABEnc import Input, Output
from secretshare import SecretShare
from charm.core.engine.util import serializeDict,objectToBytes
import random
from datetime import datetime
from openpyxl import load_workbook
from openpyxl import Workbook
from PoK import PoK
from TSPS import TSPS
from BLS import BLS01
from secretshare import SecretShare as SSS

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
    
  
    def PGen(self,k,n):
        mpk = TSPS.PGen()
        return (mpk)


    def AuKeygen(self, mpk, msk,k,n):
        (sgk_a,vk_a,pk_a) = TSPS.kgen(msk,mpk,k,n)
        return (sgk_a,vk_a,pk_a)

    def MKeygen(self,mpk,M):
        Vkm={};Skm={}
        for i in range(M):
            (vkm,skm)=BLS01.keygen(mpk['g'])
            Vkm[i]=vkm; Skm[i]=skm
        ML={'vkm':Vkm, 'skm': Skm}    
        return ML
    
    def MRegister(mpk,sgk,vkm,M,k):
        cert={}
        for i in range(M):
            sigma1=TSPS.par_sign1(mpk,vkm,k)
            sigma=TSPS.par_sign2(sigma1,sgk,k)
            sigmaR=TSPS.reconst(sigma,k)
            cert[i]=sigmaR
        return cert

    def CuKeyGen(self,mpk,C):
        Sk={}; Pk={}
        for i in range(C):
            sk=group.random(); Sk[i]=sk
            pk=mpk['g'] ** sk; Pk[i]=pk
        CL={'sk':sk, 'pk':pk}
        return CL

    def CuRegister(mpk,sgk,pk,C,k):
        cert={}
        for i in range(C):
            sigma1=TSPS.par_sign1(mpk,pk,k)
            sigma=TSPS.par_sign2(sigma1,sgk,k)
            sigmaR=TSPS.reconst(sigma,k)
            cert[i]=sigmaR
        return cert

    def CuCreate(mpk,cert,co):
        K={}; Kprime={}; Col={}
        for i in range(co):
            k=group.random();K[i]=k
            kprime=mpk['g']**k; Kprime[i]=kprime
        Col={'k':K,'kprime':Kprime}
        certprime=TSPS.Randomize(cert)
        return (Col,certprime)
    
    def AuCreate(mpk,sgk,kprime,Col,k):
        sigma1=TSPS.par_sign1(mpk,kprime,k)
        sigma=TSPS.par_sign2(sigma1,sgk,k)
        sigmaR=TSPS.reconst(sigma,k)
        Col['cert']=sigmaR
        return Col

    def Spending(self, mpk, Col, pk, time,N,ID,cert):
        r = mpk['g'] ** (1/(Col['PRFkey']+time))
        R = pair(r,mpk['h'])
        C = ID * (pair(r, mpk['pp']))
        C1 = pair(r, pk['pk'][N])
        certprime=TSPS.Randomize(cert)
        ct = { 'C': C, 'C1': C1, 'R':R }
        return (ct, certprime)


    def Verification(self, mpk, pk, Rand, L1, L2, ct, certprime, d, Ledger, time, N):
        LHS=1
        for i in range(len(ct['R'])):
            LHS *= (mpk['e_gh'] * ct['R'][i] ** (-time)) 
        if pair(Rand['Sprime'], Rand['Rprime']) == proof1['y'] * mpk['e_Xh'] ** d and \
            pair(Rand['Tprime'],Rand['Rprime']) == pair(Rand['Sprime'],mpk['vk']) * mpk['e_gh']**d and \
                LHS==proof2['y'] and \
                    L1 * (ct['C']**(-time)) == proof4['y'] and \
                    L2 * (ct['C1'] ** (-time)) == proof3['y'] and \
                    PoK.verifier3(mpk['g'],proof1['y'],proof1['z'],proof1['t'],mpk['vk']) == 1 and \
                        PoK.verifier5(proof2['y'],proof2['z'],proof2['t'],ct['R']) == 1 and \
                            PoK.verifier4(proof3['y'],proof3['z'],proof3['t'],ct['C1'],pk['pk'][N]) == 1 and \
                                PoK.verifier2(ct['C'],mpk['e_gh'],proof4['y'],proof4['z1'],proof4['z2'],proof4['t'],ct['u'])==1 and \
                                ct['R'] not in Ledger:
                Ledger.append(ct['R'])
                return Ledger
        else:
            return Ledger

    def Decryption(self, mpk, ct1, M1, ct2, M2): 
        Coeff = SSS.recoverCoefficients([group.init(ZR, M1+1),group.init(ZR, M2+1)])
        return ct2['C'] / ((ct1['C1']**Coeff[M1+1])*(ct2['C1']**Coeff[M2+1]))

