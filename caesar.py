7
def encrypt(key,plaintext):
    ciphertext=""
    #YOUR CODE HERE
    hashmap1 = {}
    for i in range(26):
        if i + key >= 26:
            hashmap1[chr(ord('A')+i)] = chr(ord('A')+(i+key)%26)
        else:
            hashmap1[chr(ord('A')+i)] = chr((ord('A')+i+key))
    # print(hashmap1)
    char_arr = list(plaintext)
    for i in range(len(char_arr)):
        char_arr[i] = hashmap1[char_arr[i]]
    ciphertext = ''.join(char_arr)
    return ciphertext

def decrypt(key,ciphertext):
    hashmap2 = {}
    for i in range(26):
        if i - key <= 0:
            hashmap2[chr(ord('A')+i)] = chr(ord('A')+(i-key)%26)
        else:
            hashmap2[chr(ord('A')+i)] = chr((ord('A')+i-key))
    # print(hashmap2)
    plaintext=""
    # #YOUR CODE HERE
    char_arr = list(ciphertext)
    for i in range(len(char_arr)):
        char_arr[i] = hashmap2[char_arr[i]]
    plaintext = ''.join(char_arr)
    return plaintext
# print(encrypt(3,"A"))
# print(decrypt(3,"A"))


