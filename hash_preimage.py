import hashlib
import os

def hash_preimage(target_string):
    def tobit(num):
        hashnum = hashlib.sha256(num).hexdigest().encode('utf-8')
        return bin(int(hashnum, 16))
    if not all( [x in '01' for x in target_string ] ):
        print( "Input should be a string of bits" )
        return
    nonce = b'\x00'

    while True:
        nonce = os.urandom(20)
        bitn = tobit(nonce)
        if bitn[-len(target_string):] == target_string:
            break
    return( nonce )
