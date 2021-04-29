from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.toolbox.secretutil import SecretUtil
from charm.toolbox.ABEnc import Input, Output
from secretshare import SecretShare
from Nirvana import Nirvana

groupObj = PairingGroup('/your/path/pbc-0.5.14/param/f.param', param_file=True) or groupObj = PairingGroup('SS512')
Nir = Nirvana(groupObj)
SSS = SecretShare(groupObj, True)
assert groupObj.InitBenchmark()
# setup
groupObj.StartBenchmark(["RealTime"])
(mpk, msk) = Nir.Setup()
groupObj.EndBenchmark()
msmtDict = groupObj.GetGeneralBenchmarks()
print("Setup phase time := ", msmtDict["RealTime"])
# Key Gen
groupObj.StartBenchmark(["RealTime","Mul", "Div", "Exp", "Granular"])
Merchants = ['Apple', 'Tesco', 'Tesla', 'Amazon', 'Bol', 'Ebay']
(pk,sk) = Nir.Keygen(mpk, msk, Merchants)
msmtDict = groupObj.GetGeneralBenchmarks()
# Registeration
n=5
(Col) = Nir.Registeration(mpk, msk, n)
print("\nCollatorels :=>", Col)

# Spending
d=5
(ct1, Rand1) = Nir.Spending(mpk, Col, pk, 1235, d, 'Apple')
print("\nFirst Ciphertext :=>\n", ct1)

(ct2, Rand2) = Nir.Spending(mpk, Col, pk, 1235, d, 'Amazon')
print("\nSecond Ciphertext :=>\n", ct2)

# Verification 
(out1)= Nir.Verification(mpk,ct1,Rand1)
print("\nIs the First Merhcnat accepted?", out1)

(out2)= Nir.Verification(mpk,ct2,Rand2)
print("\nIs the Second Merchant accepted?", out2)

# Decryption
(out)= Nir.Decryption(mpk, ct1, pk['Merlist'].index('Apple'), ct2, pk['Merlist'].index('Amazon'))
print("\n", out)
#Benchmark
groupObj.EndBenchmark()
msmtDict = groupObj.GetGeneralBenchmarks()
print("<=== General Benchmarks ===>")
print("Mul := ", msmtDict["Mul"])
print("Div := ", msmtDict["Div"])
print("Exp := ", msmtDict["Exp"])
print("RealTime := ", msmtDict["RealTime"])
granDict = group.GetGranularBenchmarks()
print("<=== Granular Benchmarks ===>")
print("G mul   := ", granDict)
