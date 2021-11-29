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


    def AuKeygen(self, mpk,k,n):
        (Sgk_a,Vk_a,Pk_a) = TSPS.kgen(mpk,k,n)
        return (Sgk_a,Vk_a,Pk_a)

    def MKeygen(self,mpk,M):
        Vk_b={};Sk_b={}
        for i in range(M):
            (vk_b,sk_b)=BLS01.keygen(mpk['g'])
            Vk_b[i]=vk_b; Sk_b[i]=sk_b    
        return (Vk_b,Sk_b)
    
    def MRegister(mpk,sgk,vkm,M,k):
        cert_b={}; Pk_b={}
        s=group.random()
        shares= SSS.genShares(s, 2, M)
        for i in range(1,M+1):
            sigma1 = TSPS.par_sign1(mpk,vkm,k)
            sigma = TSPS.par_sign2(sigma1,sgk,k)
            sigmaR = TSPS.reconst(sigma,k)
            cert_b[i]=sigmaR
            Pk_b[i]=mpk['g']**shares[i]
        return (Pk_b,cert_b)

    def CuKeyGen(self,mpk,C):
        Sk_c={}; Pk_c={}
        for i in range(C):
            sk=group.random(); Sk_c[i]=sk
            pk=mpk['g'] ** sk; Pk_c[i]=pk
        return (Sk_c,Pk_c)

    def CuRegister(mpk,Sgk_a,Pk_c,C,k):
        cert_c={}
        for i in range(C):
            sigma1=TSPS.par_sign1(mpk,Pk_c[i],k)
            sigma=TSPS.par_sign2(sigma1,Sgk_a,k)
            sigmaR=TSPS.reconst(sigma,k)
            cert_c[i]=sigmaR
        return cert_c

    def CuCreate(mpk,cert_cn):
        K={}; Kprime={}; Col={}
        k = group.random()
        kprime = mpk['g']**k
        certprime=TSPS.Randomize(cert_cn)
        return (k,kprime,certprime)
    
    def AuCreate(mpk,Sgk_a,kprime,k):
        sigma1=TSPS.par_sign1(mpk,kprime,k)
        sigma=TSPS.par_sign2(sigma1,Sgk_a,k)
        sigmaR=TSPS.reconst(sigma,k)
        cert_j=sigmaR
        return cert_j

    def Spending(self, mpk, k, pk_bm, time,N,ID,cert_j):
        r = mpk['g'] ** (1/(k+time))
        R = pair(r,mpk['h'])
        C = ID * (pair(r, mpk['pp']))
        C1 = pair(r, pk_bm)
        certprime_j = TSPS.Randomize(cert_j)
        inp = { 'C': C, 'C1': C1, 'R':R , 'cert': certprime_j}
        return (inp)


    def Verification(self, Pk_a, inp, Ledger, time, N):
        LHS=1
        if inp['R'] not in Ledger and \
            TSPS.verify(Pk_a,inp['certprime_j'])==1:
                Ledger.append(inp['R'])
                return Ledger
        else:
            return Ledger

    def Decryption(self, mpk, ct1, M1, ct2, M2): 
        Coeff = SSS.recoverCoefficients([group.init(ZR, M1+1),group.init(ZR, M2+1)])
        return ct2['C'] / ((ct1['C1']**Coeff[M1+1])*(ct2['C1']**Coeff[M2+1]))

