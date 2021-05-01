
def start_bench(group):
    group.InitBenchmark()
    group.StartBenchmark(["RealTime", "CpuTime"])

def end_bench(group, operation):
    group.EndBenchmark()
    benchmarks = group.GetGeneralBenchmarks()
    cpu_time = benchmarks['CpuTime']
    real_time = benchmarks['RealTime']
    return "%s,%f,%f" % (operation, cpu_time, real_time)

groupObj = PairingGroup('BN254')
Nir = Nirvana(groupObj)
SSS = SecretShare(groupObj, True)

def run_round_trip(n,d):


    # setup
    start_bench(groupObj)
    (mpk, msk) = Nir.Setup()
    setup_time = end_bench(groupObj, "Setup")
    public_parameters_size = len(objectToBytes(mpk, groupObj))

    # Key Gen
    start_bench(groupObj)
    Merchants = ['Apple', 'Tesco', 'Tesla', 'Amazon', 'Bol', 'Ebay']
    (pk,sk) = Nir.Keygen(mpk, msk, Merchants)
    Key_Gen_time = end_bench(groupObj, "Key Gen")


    # Registeration
    start_bench(groupObj)
    (Col) = Nir.Registeration(mpk, msk, n)
    #print("\nCollatorels :=>", Col)
    Registeration_time = end_bench(groupObj, "Registeration")

    # Spending
    start_bench(groupObj)
    (ct1, Rand1) = Nir.Spending(mpk, Col, pk, 1235, d, 'Apple')
    #print("\nFirst Ciphertext :=>\n", ct1)
    Spending_time = end_bench(groupObj, "Spending_time")
    Ciphertext_size = len(objectToBytes(ct1, groupObj))
    (ct2, Rand2) = Nir.Spending(mpk, Col, pk, 1235, d, 'Amazon')
    #print("\nSecond Ciphertext :=>\n", ct2)

    # Verification 
    start_bench(groupObj)
    (out1)= Nir.Verification(mpk,ct1,Rand1)
    #print("\nIs the First Merhcnat accepted?", out1)
    Verification_time = end_bench(groupObj, "Verification")

    #(out2)= Nir.Verification(mpk,ct2,Rand2)
    #print("\nIs the Second Merchant accepted?", out2)

    # Decryption
    start_bench(groupObj)
    (out)= Nir.Decryption(mpk, ct1, pk['Merlist'].index('Apple'), ct2, pk['Merlist'].index('Amazon'))
    print("\n", out)
    Decryption_time = end_bench(groupObj, "Decryption_time")

    return {'proxy_keygen_exec_time': setup_time,
            'encrypt_exec_time': Key_Gen_time,
            'proxy_decrypt_exec_time': Registeration_time,
            'Spending_time': Spending_time,
            'Verification_time': Verification_time,
            'decrypt_exec_time': Decryption_time
            }

for n in range(1, 2):
    result = run_round_trip(1000,1000)
    print("function,CpuTime,RealTime")
    [print(v) for v in result.values()]

