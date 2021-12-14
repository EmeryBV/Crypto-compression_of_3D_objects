import copy
import random

import Parser

from MeshData.Vertex import Vertex

from Encryption import encryption
from Evaluation import compressionEvaluation

from Compression.huffman import compresser
from Compression.ActiveList import ActiveList

listPrediction = []
predIsAdd = True

class Compression:
    def __init__(self, vertices, faces, filename):
        self.stack = []
        self.vertices = vertices
        self.triangles = faces
        self.filename = filename

    def getStartTriangle(self):
        # return self.triangles[random.randint(0,(len(self.triangles)-1))]
        return self.triangles[0]

    def encodeConnectivity(self):
        global listPrediction
        listPrediction = []
        traversalOrder = []

        startFace = self.getStartTriangle()
        startVertices = startFace.vertices

        self.encodeVertexInFile("add", vertex=startVertices[0], valence=startVertices[0].valence)
        self.encodeVertexInFile("add", vertex=startVertices[1], valence=startVertices[1].valence)
        self.encodeVertexInFile("add", vertex=startVertices[2], valence=startVertices[2].valence)

        traversalOrder.append(startVertices[0].index)
        traversalOrder.append(startVertices[1].index)
        traversalOrder.append(startVertices[2].index)

        for edge in startFace.edges:
            edge.encode()

        AL = ActiveList(startVertices.copy())
        self.stack.append(AL)

        while self.stack:

            AL = self.stack.pop()
            if not AL.vertexList:
                continue
            AL.nextFocus()
            AL.sortFocusVertexNeighbors(self.vertices, self.triangles)

            while AL.vertexList:
                print("\n")
                print("Focus vertex : ", AL.focusVertex.index )
                print("Vertex in AL = ", [n.index for n in AL.vertexList])
                for l in self.stack:
                        print( "AL in stack : ",  [ v.index for v in l.vertexList], len(l.vertexList ) )

                print("NEIGHBORS = ", [[n, self.vertices[n].isEncoded()] for n in AL.focusVertex.neighbors])

                e = AL.nextFreeEdge()
                if e:
                    u = self.vertices[AL.vertexAlongEdge(e)]
                    if not u.isEncoded():
                        print("Ajout du vertice " + str(u.index))

                        encoded = self.encodeFace(u, AL.focusVertex, AL.vertexList[len(AL.vertexList) - 1])
                        if encoded:

                            listPrediction.append([AL.focusVertex, AL.vertexList[len(AL.vertexList) - 1],
                                                   AL.vertexList[len(AL.vertexList) - 2], u])

                            self.encodeVertexInFile("add", vertex=u, valence=str(u.valence))
                            AL.addVertex(u)
                            traversalOrder.append(u.index)
                        else:
                            AL.focusVertex.edges.remove(e)

                    elif AL.contains(u):

                        self.encodeVertexInFile("split", vertex=u, offset=str(AL.getOffset(u)))
                        self.encodeFace(u, AL.focusVertex, AL.vertexList[len(AL.vertexList) - 1])

                        if AL.focusVertex.isFull():
                            self.encodeFace(AL.focusVertex, AL.vertexList[1], u )

                        ALBis = AL.split(u)

                        temp = AL.vertexList
                        if len(AL.vertexList) < len(ALBis.vertexList):
                            AL.vertexList = ALBis.vertexList
                            ALBis.vertexList = temp

                        print("Split occuring on ", u.index)
                        print("AL : ", [n.index for n in AL.vertexList] )
                        print("ALBIS : ", [n.index for n in ALBis.vertexList])
                        AL.nextFocus()
                        AL.sortFocusVertexNeighbors( self.vertices, self.triangles )
                        print("Focus vertex after split : ", AL.focusVertex.index )

                        self.stack.append(ALBis)

                    else:
                        cpt = 0
                        for AList in self.stack:
                            if AList.contains(u):
                                print("Vertex where u is found ", [n.index for n in AList.vertexList])
                                self.encodeVertexInFile("merge", vertex=u, offset=str(AL.getOffset(u)), index=cpt) # offset = numéro de AL
                                AL.merge(AList, u)
                                self.encodeFace(u, AL.focusVertex, AL.vertexList[len(AL.vertexList) - 2])

                                self.stack.remove(AList)
                                break
                            cpt += 1

                while AL.removeFullVertices( self.triangles ):
                    pass

                if AL.vertexList:
                    if AL.focusVertex.isFull():
                        AL.nextFocus()
                        print( "Next focus vertex" , AL.focusVertex.index )
                        AL.sortFocusVertexNeighbors( self.vertices, self.triangles )
                else:
                    break

        print(traversalOrder)
        line = ""
        for index in traversalOrder:
            line += " " + str(index)
        file = open(self.filename, "a")
        file.write("order" + line + "\n")
        file.close()


    def writeVertex(self, ):
        file = open(self.filename, "a")
        file.write("\n")
        file.write("v")
        for vertex in self.vertices:
            file.write("\n")
            file.write(str(int(vertex.position[0])) + " " + str(int(vertex.position[1])) + " " + str(
                int(vertex.position[2])))
        file.close()


    def writeNormal(self):
        file = open(self.filename, "a")
        file.write("\n")
        file.write("n")
        for vertex in self.vertices:
            file.write("\n")
            file.write(str(int(vertex.normal[0])) + " " + str(int(vertex.normal[1])) + " " + str(
                int(vertex.normal[2])))

        file.close()

    def writeTexture(self):
        file = open(self.filename, "a")
        file.write("\n")
        file.write("t")
        for vertex in self.vertices:
            file.write("\n")
            file.write(str(int(vertex.texture[0])) + " " + str(int(vertex.texture[1])))
        file.close()

    def encodeFace(self, v1, v2, v3):
        face = self.getFaces(v1, v2, v3)
        if not face:
            return False
        for edge in face.edges:
            if not edge.isEncoded():
                print("encode", edge.vertices)
                edge.encode()
        return True

    def encodeVertexInFile(self, instruction, vertex, valence=None, offset=None, index=None):
        global predIsAdd
        file = open(self.filename, "a")
        if instruction == "add":
            vertex.encode()
            if predIsAdd:
                line = " ".join([ str(valence)])
            else : line = " ".join([instruction, str(valence)])
            predIsAdd = True
        elif instruction == "split":
            vertex.encode()
            line = " ".join([instruction, str(offset)])
            predIsAdd = False
        else:
            vertex.encode()
            line = " ".join([instruction, str(index), str(offset)])

        print(line)
        file.write(line + "\n")
        file.close()

    def getBoundingBoxVertices(self):
        minVertice = [10000, 10000, 10000]
        maxVertice = [0, 0, 0]

        for vertex in self.vertices:
            for i in range(3):

                if vertex.position[i] < minVertice[i]:
                    minVertice[i] = vertex.position[i]
                if vertex.position[i] > maxVertice[i]:
                    maxVertice[i] = vertex.position[i]

        return minVertice, maxVertice

    def getBoundingBoxNormals(self):
        minNormal = [10000, 10000, 10000]
        maxNormal = [0, 0, 0]

        for vertex in self.vertices:
            for i in range(3):
                if vertex.normal[i] < minNormal[i]:
                    minNormal[i] = vertex.normal[i]
                if vertex.normal[i] > maxNormal[i]:
                    maxNormal[i] = vertex.normal[i]
        return minNormal, maxNormal

    def getBoundingBoxTextures(self):
        minTexture = [10000, 10000, 10000]
        maxTexture = [0, 0, 0]

        for vertex in self.vertices:
            for i in range(2):
                if vertex.texture[i] < minTexture[i]:
                    minTexture[i] = vertex.texture[i]
                if vertex.texture[i] > maxTexture[i]:
                    maxTexture[i] = vertex.texture[i]
        return minTexture, maxTexture

    def getFaces(self, v1, v2, v3):
        for face in self.triangles:
            if face.composedOf(v1, v2, v3):
                return face
        print( "No face found between" ,v1.index, v2.index, v3.index)

    def encodeGeometrySinceConnectivity(self, seed, quantification):
        keyXOR = []
        keyShuffling = []
        global listPrediction
        file = open(self.filename, "a")
        minVertices, maxVertices, minNormals,maxNormals, minTextures, maxTextures=self.quantification(quantification)
        file.write( "[" + str(minVertices[0])+";" + str(minVertices[1]) + ";" + str(minVertices[2])+"]\n")
        file.write( "[" + str(maxVertices[0])+";" + str(maxVertices[1]) + ";" + str(maxVertices[2])+"]\n")

        file.write("[" + str(minNormals[0]) + ";" + str(minNormals[1]) + ";" + str(minNormals[2]) + "]\n")
        file.write("[" + str(maxNormals[0]) + ";" + str(maxNormals[1]) + ";" + str(maxNormals[2]) + "]\n")

        if minTextures and maxTextures:
            file.write( "[" + str(minTextures[0])+";" + str(minTextures[1]) +"]\n")
            file.write( "[" + str(maxTextures[0])+";" + str(maxTextures[1]) +"]\n")

        file.write("q " + str(quantification))

        listPredictionPosition = []
        for listVertex in listPrediction:
            list = []
            for i in range(0, 3):
                list.append(listVertex[3].position[i] -
                            prediction(listVertex[0].position, listVertex[1].position, listVertex[2].position)[i])
            listPredictionPosition.append(list)

        listEncrypt = []
        listEncrypt.append(self.vertices[0].position)
        listEncrypt.append(self.vertices[1].position)
        listEncrypt.append(self.vertices[2].position)
        listEncrypt.extend(listPredictionPosition)

        for idx in range(len(listEncrypt)):
            self.vertices[idx].position = listEncrypt[idx]

        EncryptionVertices =encryption.Encrypton (self.vertices)
        keyXOR = EncryptionVertices.encodingXOR(seed,quantification)
        keyShuffling = EncryptionVertices.shufflingEncryption(seed)

        file.close()
        self.writeVertex()
        self.writeNormal()
        if minTextures and maxTextures:
            self.writeTexture()
        listPrediction = []
        return keyXOR, keyShuffling

    def encodeGeometryWithoutConnectivity(self, seed, quantification, compressFilename):
        keyXOR = None
        keyShuffling = None
        minVertices, maxVertices, minNormals,maxNormals, minTextures, maxTextures = self.quantification(quantification)
        copyVerticesQuantified = copy.deepcopy(self.vertices)

        EncryptionVertices =encryption.Encrypton (self.vertices)
        keyXOR = EncryptionVertices.encodingXOR(seed,quantification)
        keyShuffling = EncryptionVertices.shufflingEncryption(seed)


        copyVerticesQuantifiedEncrypt = copy.deepcopy(self.vertices)

        hausdorffDistanceEncryption =  compressionEvaluation.HausdorffDistance(copyVerticesQuantified, copyVerticesQuantifiedEncrypt)
        print("HAUSDORFF distance Encrypt: " + str(hausdorffDistanceEncryption))

        self.writeCompressFile(compressFilename,0)

        fileOut = open(compressFilename, 'a')
        fileOut.write("\n# "+str(quantification)+"\n")
        fileOut.write("# [" + str(minVertices[0]) + ";" + str(minVertices[1]) + ";" + str(minVertices[2]) + "]\n")
        fileOut.write("# [" + str(maxVertices[0]) + ";" + str(maxVertices[1]) + ";" + str(maxVertices[2]) + "]\n")

        fileOut.write("# [" + str(minNormals[0]) + ";" + str(minNormals[1]) + ";" + str(minNormals[2]) + "]\n")
        fileOut.write("# [" + str(maxNormals[0]) + ";" + str(maxNormals[1]) + ";" + str(maxNormals[2]) + "]\n")

        if(minTextures):
            fileOut.write("# [" + str(minTextures[0]) + ";" + str(minTextures[1]) + ";" + str(minTextures[2]) + "]\n")
            fileOut.write("# [" + str(maxTextures[0]) + ";" + str(maxTextures[1]) + ";" + str(maxTextures[2]) + "]\n")
        fileOut.close()

        with open(compressFilename, 'r') as fin:
            data = fin.read().splitlines(True)
        with open(compressFilename, 'w') as fout:
            fout.writelines(data[1:])
        return keyXOR, keyShuffling

    def writeCompressFile(self, filename, precision):
        Parser.writeMesh(self.vertices, self.triangles, filename, precision )

    def remapingVertices(self, minVertices, maxVertices):
        pointNormalize = (len(self.vertices)) * [None]
        sumExtremum = []
        for i in range(3):
            sumExtremum.append(abs(minVertices[i]) + abs(maxVertices[i]))
        l = 0
        for vertex in self.vertices:
            normalizeVertex = []
            normalizeVertex.clear()
            for i in range(0, 3):
                normalizeVertex.append((vertex.position[i] + abs(minVertices[i])) / sumExtremum[i])
            newVertex = Vertex(vertex.index, normalizeVertex.copy(), vertex.neighbors, [])
            pointNormalize[l] = newVertex
            l += 1
        return pointNormalize

    def remapingNormals(self, minNormals, maxNormals):
        pointNormalize = (len(self.vertices)) * [None]
        sumExtremum = []
        for i in range(3):
            sumExtremum.append(abs(minNormals[i]) + abs(maxNormals[i]))
        l = 0
        for vertex in self.vertices:
            normalizeNormals = []
            normalizeNormals.clear()
            for i in range(0, 3):
                normalizeNormals.append((vertex.normal[i] + abs(minNormals[i])) / sumExtremum[i])
            newVertex = 0
            newVertex = Vertex(vertex.index, vertex.position, vertex.neighbors, [], normal=normalizeNormals.copy())
            pointNormalize[l] = newVertex
            l += 1
        return pointNormalize

    def remapingTextures(self, minTexture, maxTexture):
        pointNormalize = (len(self.vertices)) * [None]
        sumExtremum = []
        for i in range(2):
            sumExtremum.append(abs(minTexture[i]) + abs(maxTexture[i]))
        l = 0
        for vertex in self.vertices:
            normalizeTexture = []
            normalizeTexture.clear()
            for i in range(0, 2):
                normalizeTexture.append((vertex.texture[i] + abs(minTexture[i])) / sumExtremum[i])
            newVertex = 0
            newVertex = Vertex(vertex.index, vertex.position, vertex.neighbors, [], normal=vertex.normal, texture=normalizeTexture.copy())
            pointNormalize[l] = newVertex
            l += 1
        return pointNormalize

    def quantifyVertices(self, pointNormalize, coefficient):
        for vertex in pointNormalize:
            verticesQuantifiePosition = []
            for i in range(3):
                verticesQuantifiePosition.append(round(vertex.position[i] * coefficient))
            self.vertices[vertex.index].position = verticesQuantifiePosition.copy()


    def quantifyNormals(self, pointNormalizeNormals, coefficient):
        for vertex in pointNormalizeNormals:
            verticesQuantifieNormals = []
            for i in range(3):
                verticesQuantifieNormals.append(round(vertex.normal[i] * coefficient))
            self.vertices[vertex.index].normal = verticesQuantifieNormals.copy()

    def quantifyTextures(self, pointNormalizeTextures, coefficient):
        for vertex in pointNormalizeTextures:
            verticesQuantifieTextures = []
            for i in range(2):
                verticesQuantifieTextures.append(round(vertex.texture[i] * coefficient))
            self.vertices[vertex.index].texture= verticesQuantifieTextures.copy()


    def quantification(self,precision):
        #VERTICES
        minVertices, maxVertices = self.getBoundingBoxVertices()
        normalizePointVertices = self.remapingVertices(minVertices, maxVertices)
        self.quantifyVertices(normalizePointVertices, precision)

        #NORMALS
        minNormals, maxNormals = self.getBoundingBoxNormals()
        normalizePointNormals = self.remapingNormals(minNormals, maxNormals)
        self.quantifyNormals(normalizePointNormals, precision)

        #TEXTURES
        minTextures = []
        maxTextures = []
        if self.vertices[0].texture is not None:
            minTextures, maxTextures = self.getBoundingBoxTextures()
            normalizePointTextures = self.remapingTextures(minTextures, maxTextures)
            self.quantifyTextures(normalizePointTextures, precision)

        return minVertices,maxVertices, minNormals,maxNormals,minTextures,maxTextures

# r = v + u - w
def prediction(vPosition, uPosition, wPosition):
    rPosition = []
    for i in range(0,3):
        rPosition.append(vPosition[i] + uPosition[i] - wPosition[i])
    return rPosition

def compressionHuffman(sourceFilename, destinationFilename):
    sourceFile = open(sourceFilename, 'r')
    data = sourceFile.read()
    compressData, tree = compresser(data)
    # print(decompresser(compressData,tree))
    # for i in range(len(compressData)):
    #     print(compressData[i])
    print("Avant : {} bits / Après : {} bits".format(len(data) * 8, len(compressData)))

    destinationFile = open(destinationFilename, 'wb+')

    dico = str(tree) + "\n$\n"
    destinationFile.write(dico.encode())
    byte_array  = convertStrToByte(compressData)
    destinationFile.write(str(len(compressData)).encode() + b"$\n"+byte_array)
    destinationFile.close()
    # engine.compress(sourceFile, destinationFile)

def convertStrToByte(string):
    byte_array = bytearray()

    for i in range(0, len(string), 8):
        byte_array.append(int(string[i:i + 8], 2))
    return byte_array