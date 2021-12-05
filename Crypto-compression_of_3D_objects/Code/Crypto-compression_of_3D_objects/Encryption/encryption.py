import random

class Encrypton:

    def __init__(self, vertexList):
        self.vertexList = vertexList

    def shufflingEncryption(self, seed):
        key = randomGenerator(seed, len(self.vertexList))
        for idx in range(len(self.vertexList)):

            for i in range(3):
                self.shuffling(self.vertexList[idx], self.vertexList[(idx + key[idx][i])%len(self.vertexList)], i)


        return key

    def shufflingDecryption(self, key):
        for idx in range(len(self.vertexList)-1,-1 , -1):
            print(self.vertexList[idx].position)
            for i in range(3):
                self.shuffling(self.vertexList[idx].position, self.vertexList[(idx + key[idx][i])%len(self.vertexList)].position, i)
            print(self.vertexList[idx].position)
            print("\n")

    def shuffling(self, vertex1, vertex2, index):
        temp = vertex1[index]
        vertex1[index] = vertex2[index]
        vertex2[index] = temp

    def encodingXOR(self, quantification):
        key = getBinaryKey(56, len(self.vertexList), quantification)
        for idx in range(len(self.vertexList)):
            for i in range(3):
                self.vertexList[idx][i] = int(bin(key[idx][i] ^ self.vertexList[idx][i]), 2)
        return key

    def decodingXOR(self, key):
        # print("/////////////////////////////////DECRYPTION////////////////////////////////")
        for idx in range(len(self.vertexList)):
            for i in range(3):
                self.vertexList[idx].position[i] = int(bin(key[idx][i] ^ int(self.vertexList[idx].position[i])), 2)


def getBinaryKey(seed, numberofVertex, quantification):
    random.seed(seed)
    key = []
    for i in range(numberofVertex):
        keyXYZ = []
        for y in range(3):
            keyXYZ.append(int(random.random() * quantification))
        key.append(keyXYZ)
    return key

def randomGenerator(seed, numberofVertex):
    random.seed(seed)
    key = []
    for i in range(numberofVertex):
        keyXYZ = []
        for y in range(3):
            keyXYZ.append(int(random.random() * 10))
        key.append(keyXYZ)
    return key

