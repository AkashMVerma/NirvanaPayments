from charm.core.engine.util import objectToBytes
from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair

class PoK1():
    def __init__(self, groupObj):
        global util, group
        group = groupObj
    def prover(self,g,y,x):
        r = group.random(ZR)
        t = g ** r
        c = group.hash(objectToBytes(y, group)+objectToBytes(t, group),ZR)
        z = c * x + r
        return { 'z':z, 't':t }        
    def verifier(self, g, y, z, t):
        c = group.hash(objectToBytes(y, group)+objectToBytes(t, group),ZR)
        if (y**c) * t == g ** z:
            return 1
        else:
            return 0

class PoK2():
    def __init__(self, groupObj):
        global util, group
        group = groupObj
    def prover(self,g,y,x,u):
        r = group.random(ZR)
        t = pair(g,u) ** r
        c = group.hash(objectToBytes(y, group)+objectToBytes(t, group)+objectToBytes(u, group),ZR)
        z = c * x + r
        return { 'z':z, 't':t }
    def verifier(self, g, y, z, t, u):
        c = group.hash(objectToBytes(y, group)+objectToBytes(t, group)+objectToBytes(u, group),ZR)
        if (y**c) * t == pair(g,u) ** z:
            return 1
        else:
            return 0

class PoK3():
    def __init__(self, groupObj):
        global util, group
        group = groupObj
    def prover(self,g,y,x,R):
        t=1; Rbyte=objectToBytes(0, group); r=[]; z=[]
        for i in range(len(x)):
            r.append(group.random(ZR))
            t *= R[i] ** r[i]
            Rbyte += objectToBytes(R[i], group)
        c = group.hash(objectToBytes(y, group) + objectToBytes(t, group) + Rbyte, ZR)
        for i in range(len(x)):
            z.append(c * x[i] + r[i])
        return { 'z':z, 't':t } 
    def verifier(self, g, y, z, t, R):
        Rbyte=objectToBytes(0,group); RHS=1
        for i in range(len(R)):
            RHS *= R[i] ** z[i]
            Rbyte += objectToBytes(R[i], group)
        c = group.hash(objectToBytes(y, group) + objectToBytes(t, group) + Rbyte, ZR)
        if (y**c) * t == RHS:
            return 1
        else:
            return 0

'''
groupObj = PairingGroup('BN254')
PoK1 = PoK1(groupObj)
PoK2 = PoK2(groupObj)
PoK3 = PoK3(groupObj)

g, h = groupObj.random(G1), groupObj.random(G2)
x = group.random(ZR)
y = g ** x


(proof1) = PoK1.prover(g,y,x)
(result1) = PoK1.verifier(g,y,proof1['z'],proof1['t'])
v = group.random(ZR)
u = h ** v
y = pair(g,u) ** x
(proof2) = PoK2.prover(g,y,x,u)
(result2) = PoK2.verifier(g,y,proof2['z'],proof2['t'],u)

X=[]; R=[]; y=1
for i in range(10):
    X.append(group.random(ZR))
    R.append(group.random(GT))
    y *= R[i] ** X[i]

(proof3) = PoK3.prover(g,y,X,R)
(result3) = PoK3.verifier(g,y,proof3['z'],proof3['t'],R)
print(result2)
'''