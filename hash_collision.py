import hashlib
import os

def hash_collision(k):
    def tobit(num):
        hashnum = hashlib.sha256(num).hexdigest().encode('utf-8')
        return bin(int(hashnum, 16))

    if not isinstance(k,int):
        print( "hash_collision expects an integer" )
        return( b'\x00',b'\x00' )
    if k < 0:
        print( "Specify a positive number of bits" )
        return( b'\x00',b'\x00' )
   
    x,y =os.urandom(60),os.urandom(60)
    bitx = tobit(x)

    while True:
        y = os.urandom(60)
        bity = tobit(y)
        if bitx[-k:] == bity[-k:]:
            break

    return( x, y )
print(hash_collision(10))