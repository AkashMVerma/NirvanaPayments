from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.toolbox.secretutil import SecretUtil
from charm.toolbox.ABEnc import ABEnc, Input, Output
from secretshare import SecretShare

mpk_t = { 'g':G1, 'h':G2, 'pp': G2, 'e_gg':GT, 'vk':G2 , 'X': G1}
msk_t = { 'sec':ZR, 'sgk':ZR }
pk_t = { 'pk':G2, 'Merlist':str }
sk_t = { 'sk':ZR }
Col_t = { 'PRFkey': ZR, 'key':G1, 'R':G2, 'S':G1, 'T':G1, 'W':G1 }
Rand_t = { 'Rprime':G2, 'Sprime':G1, 'Tprime':G1, 'Wprime':G1}
ct_t = { 'C':GT, 'C1':GT }
class Nirvana(ABEnc):
         
    def __init__(self, groupObj):
        ABEnc.__init__(self)
        global util, group
        util = SecretUtil(groupObj, verbose=False)
        group = groupObj
    
    @Output(mpk_t, msk_t)    
    def Setup(self):
        g, h, sec, sgk = group.random(G1), group.random(G2), group.random(ZR), group.random(ZR)
        g.initPP(); h.initPP()
        pp = h ** sec; e_gg = pair(g,h)
        vk = h ** sgk; X = group.random(G1)
        mpk = {'g':g, 'h':h, 'pp':pp, 'e_gg':e_gg, 'vk': vk, 'X': X}
        msk = {'sec':sec, 'sgk':sgk }
        return (mpk, msk)

    @Input(mpk_t, [str])
    @Output(pk_t, sk_t)
    def Keygen(self, mpk, Merchants):
        pkey = {}
        shares = SSS.genShares(msk['sec'], 2, len(Merchants))
        print("\nSecret\n =>", msk['sec'])
        for i in range(len(shares)-1):
            pkey[i] = mpk['h'] ** shares[i+1]
        pk = {'pk': pkey, 'Merlist': Merchants}
        sk = {'shares':shares}
        return (pk, sk)

    @Input(mpk_t, msk_t, int)
    @Output(Col_t)
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

    @Input(mpk_t, Col_t, pk_t, int, int, int)
    @Output(Rand_t, ct_t)
    def Spending(self, mpk, Col, pk, time, d ,M):
        SAgg=1; TAgg=1; PRFkey=0; key=1
        if len(Col['PRFkey']) >= d:
            for i in range(d):
                SAgg *= Col['S'][i]
                TAgg *= Col['T'][i]
                PRFkey += Col['PRFkey'][i]
                key *= Col['key'][i]
            tprime = group.random(ZR)
            Rprime = Col['R'] ** (1/tprime)
            Sprime = SAgg ** tprime
            Tprime = (TAgg ** (tprime**2))* (Col['W']**(d*tprime*(1-tprime)))
            Wprime = Col['W'] ** (1/tprime)
            r = mpk['g'] ** (1/(PRFkey+time))
            ID = group.random(GT)
            C = ID * (pair(r, mpk['pp']))
            C1 = pair(r, pk['pk'][M-1])
            Rand = { 'key': key, 'Rprime':Rprime, 'Sprime':Sprime, 'Tprime':Tprime, 'Wprime':Wprime, 'd':d }
            ct = {'C': C, 'C1': C1}
            return (ct,Rand)
        else:
            return (print("You don't have enough money in your account"), None)

    @Input(mpk_t, ct_t, Rand_t)
    @Output(int)
    def Verification(self, mpk, ct, Rand): 
        if pair(Rand['Sprime'], Rand['Rprime'])==pair(Rand['key'],mpk['vk'])*pair(mpk['X'],(mpk['h']**Rand['d'])) and \
            pair(Rand['Tprime'],Rand['Rprime'])==pair(Rand['Sprime'],mpk['vk'])*pair(mpk['g']**Rand['d'],mpk['h']):
            return 1
        else:
            return 0

    @Input(mpk_t, ct_t, ct_t)
    @Output(GT)
    def Decryption(self, mpk, ct1, ct2): 
        Coeff = SSS.recoverCoefficients([group.init(ZR, 1),group.init(ZR, 2)])
        return ct1['C']/ ((ct1['C1']**Coeff[1])*(ct2['C2']**Coeff[2]))

groupObj = PairingGroup('SS512')
Nir = Nirvana(groupObj)
SSS = SecretShare(groupObj, True)

# setup
(mpk, msk) = Nir.Setup()

# Key Gen
Merchants = ['Apple', 'Tesco', 'Tesla', 'Amazon', 'Bol', 'Ebay']
(pk,sk) = Nir.Keygen(mpk, Merchants)

# Registeration
(Col) = Nir.Registeration(mpk, msk, 1)
print("\nCollatorel :=>", Col)
# Spending
(ct1, Rand1) = Nir.Spending(mpk, Col, pk, 1235, 1, 1)
print("\nFirst Ciphertext :=>\n", ct1)

(ct2, Rand2) = Nir.Spending(mpk, Col, pk, 1235, 1, 2)
print("\nSecond Ciphertext :=>\n", ct2)

# Verification 
(out1)= Nir.Verification(mpk,ct1,Rand1)
print("\nIs the First Merhcnat accepted?", out1)
(out2)= Nir.Verification(mpk,ct2,Rand2)
print("\nIs the Second Merchant accepted?", out2)

(out)= Nir.Decryption(mpk,ct1,ct2)
print("\n", out)