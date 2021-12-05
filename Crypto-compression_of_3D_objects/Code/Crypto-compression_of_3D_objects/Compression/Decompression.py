import Parser
from MeshData.Face import Face
from MeshData.Vertex import Vertex
from Compression.ActiveList import ActiveList
import re
from Compression.markov import Engine
from Encryption import encryption
listPrediction = []


class Decompression:

    def __init__(self, filenameIN, filenameOut,keyXOR, keyShufffling):
        self.stack = []
        self.vertices = []
        self.triangles = []
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
        while self.stack:
            AL = self.stack.pop(len(self.stack) - 1)
            AL.focusVertex = vertex1
            command = file.readline()

            while AL.vertexList or "order" not in command:
                print("command ", i, " ", command)
                if not AL.focusVertex.isValenceFull():
                    print("FOCUS VERTEX = ", AL.focusVertex.index)
                    if "add" in command:
                        print("AJOUT DE " + str(i))

                        print("ACTIVE LIST", [n.index for n in AL.vertexList])
                        newVertex = Vertex(i, position=[], neighbors=[], edges=[], valence=convertToInt(command))
                        listPrediction.append([AL.focusVertex, AL.vertexList[len(AL.vertexList) - 1],
                                               AL.vertexList[len(AL.vertexList) - 2]])

                        AL.makeConnectivity(newVertex)
                        self.vertices.append(newVertex)
                        print("FOCUS: Voisin= ", [n.index for n in AL.focusVertex.neighbors])
                        print("FOCUS: Edge  = ", [n.vertices for n in AL.focusVertex.edges])
                        print("newVertex: Voisin= ", [n.index for n in newVertex.neighbors])
                        print("newVertex: Edge= ", [n.vertices for n in newVertex.edges], "\n")
                        i += 1
                    command = file.readline()

                AL.removeFullVerticesValence()
                print([o.index for o in AL.vertexList])
                if AL.vertexList:
                    if AL.focusVertex.isValenceFull():
                        AL.focusVertex = AL.vertexList[0]
                        AL.makeConnectivity(AL.vertexList[len(AL.vertexList) - 1], append=False)
                        print("Last edge ", [AL.focusVertex.index, AL.vertexList[len(AL.vertexList) - 1].index])
                else:
                    break

            if "order" in command:
                self.associateCorrectIndex(command)

            self.decodeGeometry(file)
            self.orderVerticeList()

            self.makeTriangle()
            # for triangle in self.triangles:
            #     print("position= ", [n.index for n in triangle.vertices])
            self.writeDecompressFile(self.filenameOut)

    def makeTriangle(self):
        for vertex in self.vertices:
            for vertexNeigh in vertex.neighbors:
                for vertex1Neighbors in vertexNeigh.neighbors:

                    if vertex1Neighbors in vertexNeigh.neighbors and vertex1Neighbors in vertex.neighbors:
                        # print(vertex.index)
                        # print(vertex.neighbors[vertexNeigh - 1].index)
                        # print(vertex.neighbors[vertexNeigh].index)
                        # print("\n")
                        triangle = [vertex, vertex1Neighbors, vertexNeigh]
                        if not self.alreadyContainTriangle(triangle):
                            self.triangles.append(Face(triangle))


    def decryption(self):
        decryption  =encryption.Encrypton (self.vertices)
        # decryption.shufflingDecryption(self.keyShuffling)
        # decryption.decodingXOR(self.keyXOR)

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
        quantification = convertToInt(command)
        print("quantification " + str(quantification))

        self.associateCorrectCoord(file, quantification, BBvMin, BBvMax)
        self.associateCorrectNormal(file, quantification, BBvMin, BBvMax)

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
            # print(vertexquantizePosition)
            vertex.normal = vertexquantizeNormal

    def orderVerticeList(self):
        change = True
        while change:
            change = False
            for i in range(1, len(self.vertices)):
                # print(self.vertices[i-1].index)
                # print(self.vertices[i].index)
                if self.vertices[i - 1].index > self.vertices[i].index:
                    temp = self.vertices[i - 1]
                    self.vertices[i - 1] = self.vertices[i]
                    self.vertices[i] = temp
                    change = True

    def associateCorrectIndex(self, command):
        traverselOrder = convertToListInt(command)

        for i in range(len(traverselOrder)):
            # print(self.vertices[i].index)
            # print(traverselOrder[i])
            # print("\n")
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

    def writeDecompressFile(self, filename):
        Parser.writeMesh(self.vertices, self.triangles, filename)

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

def decompressionMarkov(sourceFilename, destinationFilename):
    sourceFile = open(sourceFilename, 'rb')
    destinationFile = open(destinationFilename, 'wb')
    engine = Engine()
    engine.decompress(sourceFile, destinationFile)
    # engine.decompress(sys.stdin, sys.stdout)