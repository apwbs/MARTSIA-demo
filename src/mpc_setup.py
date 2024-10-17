import hashlib

def commit(group, g1, g2):
    h1 = hashlib.sha256(group.serialize(g1)).hexdigest()
    h2 = hashlib.sha256(group.serialize(g2)).hexdigest()
    return h1, h2

def generateParameters(group, hashes1, hashes2, com1, com2):
    for i in range(len(hashes1)):
        if (hashes1[i] != hashlib.sha256(group.serialize(com1[i])).hexdigest()) or \
                (hashes2[i] != hashlib.sha256(group.serialize(com2[i])).hexdigest()):
            raise Exception("Someone cheated! The hashes don't match the commitments!" + str(i))
        
    value1 = 1
    value2 = 1
    for i in range(0, len(com1)):  # XOR bit a bit
        value1 = value1 * com1[i]
        value2 = value2 * com2[i]
    return value1, value2