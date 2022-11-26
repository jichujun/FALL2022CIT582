from zksk import Secret, DLRep
from zksk import utils

def ZK_equality(G,H):

    #Generate two El-Gamal ciphertexts (C1,C2) and (D1,D2)
    r1 =Secret(utils.get_random_num(bits=128))
    # r1_prime =Secret(utils.get_random_num(bits=128))
    r2 =Secret(utils.get_random_num(bits=128))
    # r2_prime = Secret(utils.get_random_num(bits=128))
    m = Secret(utils.get_random_num(bits=128))

    #Generate a NIZK proving equality of the plaintexts
    C1 = r1.value * G
    C2 = m.value * G + r1.value * H

    D1 = r2.value * G
    D2 = m.value * G + r2.value * H
    s = DLRep(C1, r1 * G, simulated=True) & DLRep(C2 , r1 * H + m*G) & DLRep(D1, r2 * G, simulated=True) & DLRep(D2, r2 * H + m*G) 

    #Return two ciphertexts and the proof
    zk_proof = s.prove()
    return (C1,C2), (D1,D2), zk_proof

