import ast
import json
import sys

import Parser
from MeshData.Face import Face
from MeshData.Vertex import Vertex
from Compression.ActiveList import ActiveList
import re
from Compression.huffman import decompresser
import math
# from Compression.markov import Engine
from Encryption import encryption

listPrediction = []
from bitstring import BitArray


class Decompression:

    def __init__(self, filenameIN, filenameOut, keyXOR, keyShufffling, vertices=None, triangles=None,):
        if triangles is None:
            triangles = []
        if vertices is None:
            vertices = []
        self.stack = []
        self.vertices = vertices
        self.triangles = triangles
        self.filenameIN = filenameIN
        self.filenameOut = filenameOut
        self.keyXOR = keyXOR
        self.keyShuffling = keyShufffling

    def initFirstTriangle(self, v1, v2, v3):

        v1.addNeighbors([v2, v3])
        v2.addNeighbors([v3])

        v1.addEdge([v2, v3])
        v2.addEdge([v3])

    def decodeConnectivity(self):
        global listPrediction
        listPrediction = []
        file = open(self.filenameIN, 'r')
        v1 = file.readline()
        v2 = file.readline()
        v3 = file.readline()

        vertex1 = Vertex(0, [], [], None, convertToInt(v1))
        vertex2 = Vertex(1, [], [], None, convertToInt(v2))
        vertex3 = Vertex(2, [], [], None, convertToInt(v3))
        self.vertices.extend([vertex1, vertex2, vertex3])

        self.initFirstTriangle(vertex1, vertex2, vertex3)

        AL = ActiveList([vertex1, vertex2, vertex3])
        self.stack.append(AL)
        i = 3
        command = file.readline()

        while self.stack:
            AL = self.stack.pop()
            AL.focusVertex = vertex1

            while AL.vertexList or "order" not in command:

                print("command ", i + 1, " ", command)
                print("FOCUS VERTEX = ", AL.focusVertex.index, AL.focusVertex.valence, len(AL.focusVertex.edges))
                if "add" in command or int(command)!=None:
                    print("AJOUT DE " + str(i))
                    print("ACTIVE LIST", [[n.index, n.valence, len( n.edges )] for n in AL.vertexList])

                    newVertex = Vertex(i, position=[], neighbors=[], edges=[], valence=convertToInt(command))
                    listPrediction.append([AL.focusVertex, AL.vertexList[len(AL.vertexList) - 1],
                                           AL.vertexList[len(AL.vertexList) - 2]])

                    AL.makeConnectivity(AL.focusVertex, newVertex)
                    self.vertices.append(newVertex)
                    print("FOCUS: Voisin= ", [n.index for n in AL.focusVertex.neighbors])
                    print("FOCUS: Edge  = ", [n.vertices for n in AL.focusVertex.edges])
                    print("newVertex: Voisin= ", [n.index for n in newVertex.neighbors])
                    print("newVertex: Edge= ", [n.vertices for n in newVertex.edges], "\n")
                    i += 1
                    if "order" not in command:
                        command = file.readline()

                elif "split" in command:

                    ALBis, splitVertex = AL.splitDecompression(convertToInt(command))
                    print("Split vertex : ", str(splitVertex.index))
                    AL.makeConnectivity(AL.focusVertex, splitVertex, append = False )  # connect previous focus with splitvertex

                    if AL.focusVertex.isFull():
                        AL.encodeFace2(AL.focusVertex, AL.vertexList[1],
                                         splitVertex)

                    listPrediction.append([AL.focusVertex, AL.vertexList[len(AL.vertexList) - 1],
                                           AL.vertexList[len(AL.vertexList) - 2]])


                    temp = AL.vertexList
                    if len(AL.vertexList) < len(ALBis.vertexList):
                        AL.vertexList = ALBis.vertexList
                        ALBis.vertexList = temp

                    AL.nextFocus()
                    print("FOCUS: Voisin= ", [n.index for n in AL.focusVertex.neighbors])
                    print("FOCUS: Edge  = ", [n.vertices for n in AL.focusVertex.edges])
                    print("Split : ", str(convertToInt(command)), [o.index for o in AL.vertexList],
                          [o.index for o in ALBis.vertexList])

                    self.stack.append(ALBis)

                    if "order" not in command:
                        command = file.readline()

                elif "merge" in command:
                    args = convertToListInt(command)
                    print( args )

                    AL.mergeDecompression( self.stack.pop(int(args[0])), int(args[1]) )
                    AL.makeConnectivity(AL.focusVertex, AL.vertexList[int(args[1])], append = False )

                    if "order" not in command:
                        command = file.readline()

                while AL.removeFullVerticesValence():
                    pass

                print("AL : ", [o.index for o in AL.vertexList], len(AL.vertexList ))
                for l in self.stack:
                        print( "AL in stack : ",  [ v.index for v in l.vertexList], len(l.vertexList ) )

                if AL.vertexList:
                    if AL.focusVertex.isValenceFull():
                        AL.nextFocus()
                        # AL.makeConnectivity(AL.focusVertex, AL.vertexList[len(AL.vertexList) - 1], append=False)
                else:
                    break

        if "order" not in command:
            command = file.readline()

        if "order" in command:
            self.associateCorrectIndex(command)

        precision = self.decodeGeometry(file)

        self.orderVerticeList()
        self.makeTriangle()
        self.writeDecompressFile(self.filenameOut, precision)

    def makeTriangle(self):
        for vertex in self.vertices:
            for vertexNeigh in vertex.neighbors:
                for vertex1Neighbors in vertexNeigh.neighbors:

                    if vertex1Neighbors in vertexNeigh.neighbors and vertex1Neighbors in vertex.neighbors:

                        triangle = [vertex, vertex1Neighbors, vertexNeigh]
                        if not self.alreadyContainTriangle(triangle):
                            self.triangles.append(Face(triangle))

    def decryption(self):
        decryption = encryption.Encrypton(self.vertices)

        decryption.shufflingDecryption(self.keyShuffling)
        decryption.decodingXOR(self.keyXOR)

    def decodeGeometry(self, file):
        command = file.readline()
        BBvMin = convertToListInt(command)
        print("BBvmin" + str(BBvMin))

        command = file.readline()
        BBvMax = convertToListInt(command)
        print("BBvMax" + str(BBvMax))

        command = file.readline()
        BBnMin = convertToListInt(command)
        print("BBnmin" + str(BBnMin))

        command = file.readline()
        BBnMax = convertToListInt(command)
        print("BBnMax" + str(BBnMax))

        command = file.readline()
        BBtMin = convertToListInt(command)
        print("BBtmin" + str(BBtMin))

        command = file.readline()
        BBtMax = convertToListInt(command)
        print("BBtMax" + str(BBtMax))

        command = file.readline()
        quantification = convertToInt(command)
        print("quantification " + str(quantification))

        command = file.readline()
        if "v" in command:
            self.associateCorrectCoord(file, quantification, BBvMin, BBvMax)
        command = file.readline()
        if "n" in command:
            self.associateCorrectNormal(file, quantification, BBvMin, BBvMax)
        command = file.readline()
        if "t" in command:
            self.associateCorrectTexture(file, quantification, BBtMin, BBtMax)

        return precision_and_scale(float(BBnMin[0]))

    def decodeGeometryNotSinceConnectivity(self):

        haveTexture = False
        minTexture = []
        maxTexture = []
        f1 = open(self.filenameIN, "r")
        listLine = f1.readlines()
        if len(convertToListInt(listLine[-7])) == 1:
            maxTexture = convertToListInt(listLine[-1])
            minTexture = convertToListInt(listLine[-2])
            maxNormal = convertToListInt(listLine[-3])
            minNormal = convertToListInt(listLine[-4])
            maxVertices = convertToListInt(listLine[-5])
            minVertices = convertToListInt(listLine[-6])
            quantification = convertToInt(listLine[-7])
            haveTexture = True

        else :
            maxNormal = convertToListInt(listLine[-1])
            minNormal = convertToListInt(listLine[-2])
            maxVertices = convertToListInt(listLine[-3])
            minVertices = convertToListInt(listLine[-4])
            quantification = convertToInt(listLine[-5])
        f1.close()

        self.decryption()
        # self.writeDecompressFile("test.obj",10)
        self.dequantificationVertices(quantification)
        self.dequantificationNormals(quantification)
        if haveTexture:
            self.dequantificationTextures(quantification)

        self.remapingInvVertices(minVertices,maxVertices)
        self.remapingInvNormals(minNormal,maxNormal)
        if haveTexture:
            self.remapingInvTextures(minTexture,maxTexture)

        self.writeDecompressFile(self.filenameOut,0)

    def getBoundingBoxVertices(self):
        minVertice = [10000, 10000, 10000]
        maxVertice = [0, 0, 0]
        for vertex in self.vertices:
            for i in range(3):
                if int(vertex.position[i]) < int(minVertice[i]):
                    minVertice[i] = int(vertex.position[i])
                if int(vertex.position[i]) > int(maxVertice[i]):
                    maxVertice[i] = int(vertex.position[i])
        return minVertice, maxVertice

    def dequantificationVertices(self, coefficient):
        for vertex in self.vertices:
            verticesDequantifiePosition = []
            for i in range(3):
                verticesDequantifiePosition.append(float(vertex.position[i]) / float(coefficient))
            vertex.position = verticesDequantifiePosition

    def dequantificationNormals(self, coefficient):
        for vertex in self.vertices:
            verticesDequantifieNormals = []
            for i in range(3):
                verticesDequantifieNormals.append(float(vertex.normal[i]) / float(coefficient))
            vertex.normal = verticesDequantifieNormals

    def dequantificationTextures(self, coefficient):
        for vertex in self.vertices:
            verticesDequantifieTextures = []
            for i in range(2):
                verticesDequantifieTextures.append(float(vertex.texture[i]) / float(coefficient))
            vertex.texture = verticesDequantifieTextures

    def remapingInvVertices(self, minVertex, maxVertex):
        for vertex in self.vertices:
            vertexquantizePosition = []
            for i in range(3):
                vertexquantizePosition.append(
                    float(vertex.position[i]) * (abs(float(minVertex[i])) + abs(float(maxVertex[i]))) - abs(
                        float(minVertex[i])))
            vertex.position = vertexquantizePosition

    def remapingInvNormals(self, minNormal, maxNormal):
        for vertex in self.vertices:
            vertexquantizeNormal = []
            for i in range(3):
                vertexquantizeNormal.append(
                    float(vertex.normal[i]) * (abs(float(minNormal[i])) + abs(float(maxNormal[i]))) - abs(
                        float(minNormal[i])))
            vertex.normal = vertexquantizeNormal

    def remapingInvTextures(self, minTextures, maxTextures):
        for vertex in self.vertices:
            vertexquantizeTexture = []
            for i in range(2):
                vertexquantizeTexture.append(
                    float(vertex.texture[i]) * (abs(float(minTextures[i])) + abs(float(maxTextures[i]))) - abs(
                        float(minTextures[i])))
            vertex.texture = vertexquantizeTexture

    def orderVerticeList(self):
        change = True
        while change:
            change = False
            for i in range(1, len(self.vertices)):

                if self.vertices[i - 1].index > self.vertices[i].index:
                    temp = self.vertices[i - 1]
                    self.vertices[i - 1] = self.vertices[i]
                    self.vertices[i] = temp
                    change = True

    def associateCorrectIndex(self, command):
        traverselOrder = convertToListInt(command)

        for i in range(len(traverselOrder)):
            self.vertices[i].index = int(traverselOrder[i])

    def alreadyContainTriangle(self, triangleList):
        for triangle in self.triangles:
            if triangleList[0] in triangle.vertices and triangleList[1] in triangle.vertices and triangleList[
                2] in triangle.vertices:
                return True
        return False

    def associateCorrectCoord(self, file, quantification, BBvMin, BBvMax):
        for vertex in self.vertices:
            command = file.readline()
            position = convertToListInt(command)
            vertex.position = position
        j = 0
        self.decryption()
        for i in range(3, len(self.vertices)):
            self.vertices[i].position = findVertexWithprediction(listPrediction[j], self.vertices[i].position)
            j += 1

        self.dequantificationVertices(quantification)
        self.remapingInvVertices(BBvMin, BBvMax)

    def associateCorrectNormal(self, file, quantification, BBnMin, BBnMax):
        for vertex in self.vertices:
            command = file.readline()
            normal = convertToListInt(command)
            vertex.normal = normal

        self.dequantificationNormals(quantification)
        self.remapingInvNormals(BBnMin, BBnMax)

    def associateCorrectTexture(self, file, quantification, BBtMin, BBtMax):
        for vertex in self.vertices:
            command = file.readline()
            texture = convertToListInt(command)
            vertex.texture = texture

        self.dequantificationTextures(quantification)
        self.remapingInvTextures(BBtMin, BBtMax)

    def writeDecompressFile(self, filename, precision):
        Parser.writeMesh(self.vertices, self.triangles, filename, 5)

    # def repairMesh(self):
    #     for triangle in self.triangles:


def convertToInt(instruction):
    return int(re.findall(r"[-+]?\d*\.\d+|\d+", instruction)[0])


def convertToListInt(instruction):
    return re.findall(r"[-+]?\d*\.*\d+", instruction)


def findVertexWithprediction(listPrediction, prediction):
    focus = listPrediction[0]
    beforeLast = listPrediction[2]
    last = listPrediction[1]

    rPosition = []

    for i in range(0, 3):
        rPosition.append(
            (int(focus.position[i]) + int(last.position[i]) - int(beforeLast.position[i]) + int(prediction[i])))
    return rPosition


def decompressionHuffman(sourceFilename, destinationFilename):
    data, tree = parserCompressionHuffman(sourceFilename)
    decompressData = decompresser(data, tree)
    file = open(destinationFilename, 'w')
    file.write(decompressData)
    # engine = Engine()
    # engine.decompress(sourceFile, destinationFile)
    # engine.decompress(sys.stdin, sys.stdout)


def precision_and_scale(x):
    max_digits = 14
    int_part = int(abs(x))
    magnitude = 1 if int_part == 0 else int(math.log10(int_part)) + 1
    if magnitude >= max_digits:
        return (magnitude, 0)
    frac_part = abs(x) - int_part
    multiplier = 10 ** (max_digits - magnitude)
    frac_digits = multiplier + int(multiplier * frac_part + 0.5)
    while frac_digits % 10 == 0:
        frac_digits /= 10
    scale = int(math.log10(frac_digits))

    return magnitude


def parserCompressionHuffman(filename):
    file = open(filename, 'rb+')
    byte_array_tree = bytearray()
    byte = bytes
    while byte := file.read(1):
        if '$' in str(byte):
            break
        byte_array_tree.append(int.from_bytes(byte, byteorder=sys.byteorder))

    file.read(1)
    lenghtData = ""
    while byte := file.read(1):
        if '$' in str(byte):
            break
        lenghtData += byte.decode()

    file.read(1)

    nbrOctet = int(int(lenghtData) / 8)
    reste = int(int(lenghtData) % 8)
    byte_array_data = bytearray()
    # f.readlines().decode('UTF-8')
    while byte := file.read(1):
        byte_array_data.append(int.from_bytes(byte, byteorder=sys.byteorder))
    data = ""
    for i in range(len(byte_array_data)):
        if i != nbrOctet :
            data += str(bin(byte_array_data[i])[2:].zfill(8))
        else:
            data += str(bin(byte_array_data[i])[2:].zfill(reste))

    tree = byte_array_tree.decode()[1:-2].replace('\'', '')

    tree = re.split("[,:]+", tree)
    for i in range(len(tree)):
        if tree[i] =='  ' and len(tree[i]) == 2  or tree[i] ==' ' and len(tree[i]) == 1 :  # space case
            tree[i] = " "
        else:
            tree[i] = tree[i].replace(' ', "").replace("\\n", "\n")

    treeDico = convert(tree)
    return data, treeDico


def convert(lst):
    res_dct = {}
    for i in range(0, len(lst) - 1, 2):
        res_dct[str(lst[i])] = lst[i + 1]
    return res_dct
