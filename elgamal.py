import random

from params import p
from params import g

def keygen():
    q = (p-1)//2
    sk = random.randint(1,q)
    pk = pow(g,sk,mod = p) 
    return pk,sk

def encrypt(pk,m):
    q = (p-1)//2
    r = random.randint(1,q)
    c1 = pow(g,r,mod = p)
    c2=  (pow(pk,r,p) * (m%p))%p
    return [c1,c2]

def decrypt(sk,c):
    c1,c2 = c
    m = pow(c1,-sk,p) *c2
    m = pow(m,1,p)
    return m
