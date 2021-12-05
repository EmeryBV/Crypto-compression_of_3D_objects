from MeshData.Vertex import Vertex
from Compression.ActiveList import ActiveList
from Compression.markov import Engine
from Encryption import encryption
import copy
listPrediction = []
class Compression:
    def __init__(self, vertices, faces, filename):
        self.stack = []
        self.vertices = vertices
        self.triangles = faces
        self.filename = filename

    def getStartTriangle(self):
        return self.triangles[0]

    def encodeConnectivity(self):
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

            AL = self.stack.pop(len(self.stack) - 1)
            AL.nextFocus()

            AL.sortFocusVertexNeighbors(self.vertices)

            while AL.vertexList:
                print("\n")
                print("FOCUS VERTEX = ", AL.focusVertex.index)
                print("Vertex in AL = ", [n.index for n in AL.vertexList])
                print("NEIGHBORS = ", [n for n in AL.focusVertex.neighbors])

                e = AL.nextFreeEdge()
                if e:

                    u = self.vertices[AL.vertexAlongEdge(e)]

                    if not u.isEncoded():
                        print("Ajout du vertice " + str(u.index))
                        listPrediction.append([AL.focusVertex,AL.vertexList[len(AL.vertexList) - 1],AL.vertexList[len(AL.vertexList) - 2], u])

                        self.encodeFace(u, AL.focusVertex, AL.vertexList[len(AL.vertexList) - 1])
                        self.encodeVertexInFile("add", vertex=u, valence=str(u.valence))

                        AL.addVertex(u)
                        traversalOrder.append(u.index)
                        # encodedeGeometry(AL)

                    elif AL.contains(u):
                        ALBis = AL.split(u)
                        print("Split occuring on ", u.index)
                        # print("AL : ", [k.index for k in AL.vertexList], "ALBis : ", [k.index for k in ALBis.vertexList])
                        self.stack.append(ALBis)
                        self.encodeVertexInFile("split", vertex=u, offset=str(AL.getOffset(u)))

                    else:
                        for AList in self.stack:
                            if AList.contains(u):
                                print("Vertex where u is found ", [n.index for n in AList.vertexList])
                                self.encodeVertexInFile("merge", vertex=u, index=u.index, offset=str(AL.getOffset(u)))
                                AL.merge(AList, u)
                                # AL = AList
                                self.stack.remove(AList)
                                break

                    # for vertex in self.vertices:
                    #     if vertex.isFull():
                    #         valenceVertex = int(vertex.valence)
                    #         for k in range(0, valenceVertex):
                    #             vertex2 = self.vertices[vertex.neighbors[k - 1]]
                    #             vertex3 = self.vertices[vertex.neighbors[k]]
                    #             if not vertex2.getEdge(vertex2, vertex3).isEncoded() and not vertex2.isFull() and not vertex3.isFull():
                    #                 self.encodeFace(vertex, vertex2, vertex3)

                AL.removeFullVertices()

                # for AL2 in self.stack:
                #     AL2.removeFullVertices()
                if AL.vertexList:
                    if AL.focusVertex.isFull():
                        self.encodeFace(AL.focusVertex, AL.vertexList[0], AL.vertexList[len(AL.vertexList) - 1])
                        AL.nextFocus()
                        print("Next focus vertex", AL.focusVertex.index)
                        AL.sortFocusVertexNeighbors(self.vertices)
                else:
                    break

        print(traversalOrder)
        line = ""
        for index in traversalOrder:
            line += "".join(str(index)) + " "
        file = open(self.filename, "a")
        file.write("order " + line + "\n")
        file.close()

    def writeNormal(self, listQuantifiedNormals):
        file = open(self.filename, "a")

        for vertex in listQuantifiedNormals:
            line = ""
            for i in range(0, 3):
                line += "".join(str(vertex.normal[i])) + " "
            file.write("n " + line + "\n")

        file.close()

    def encodeFace(self, v1, v2, v3):
        face = self.getFaces(v1, v2, v3)
        # if face is not None and v1 != v2 and v2 != v3 and v1 != v3:
        for edge in face.edges:
            if not edge.isEncoded():
                print("encode", edge.vertices)
                edge.encode()

    def encodeVertexInFile(self, instruction, vertex, valence=None, offset=None, index=None):
        file = open(self.filename, "a")
        if instruction == "add":
            vertex.encode()
            line = " ".join([instruction, str(valence)])
        elif instruction == "split":
            line = " ".join([str(vertex.index), instruction, str(offset)])
        else:
            line = " ".join([str(vertex.index), instruction, str(index), str(offset)])

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
        # print(minVertice)
        # print(maxVertice)
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
            for i in range(3):
                if vertex.normal[i] < minTexture[i]:
                    minTexture[i] = vertex.normal[i]
                if vertex.normal[i] > maxTexture[i]:
                    maxTexture[i] = vertex.normal[i]
        return minTexture, maxTexture

    def getFaces(self, v1, v2, v3):
        for face in self.triangles:
            if face.composedOf(v1, v2, v3):
                return face

    def encodeGeometry(self, seed,quantification):
        keyXOR = None
        keyShuffling = None
        file = open(self.filename, "a")
        quantifiedVertices, quantifiedNormals = self.quantification(quantification)
        file.write("q " + str(quantification) + "\n")

        listPredictionPosition = []
        for listVertex in listPrediction:
            list = []
            for i in range(0, 3):
                list.append(listVertex[3].position[i] -
                            prediction(listVertex[0].position, listVertex[1].position, listVertex[2].position)[i])
            listPredictionPosition.append(list)

        listEncrypt = []
        listEncrypt.append(copy.deepcopy(self.vertices[0].position))
        listEncrypt.append(copy.deepcopy(self.vertices[1].position))
        listEncrypt.append(copy.deepcopy(self.vertices[2].position))
        listEncrypt.extend(listPredictionPosition)

        EncryptionVertices =encryption.Encrypton (listEncrypt)
        keyXOR = EncryptionVertices.encodingXOR(seed,quantification)
        keyShuffling = EncryptionVertices.shufflingEncryption(seed)

        for predictionPosition in listEncrypt:
            file.write("v ")
            for i in range(3):
                file.write(str(int(predictionPosition[i])) + " ")
            file.write("\n")
        file.close()

        self.writeNormal(quantifiedNormals)
        return keyXOR, keyShuffling


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
            newVertex = 0
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

    def quantifyVertices(self, pointNormalize, coefficient):
        quantifiedVertices = len(pointNormalize) * [None]
        l = 0
        for vertex in pointNormalize:
            verticesQuantifiePosition = []
            for i in range(3):
                verticesQuantifiePosition.append(round(vertex.position[i] * coefficient))

            vertexQuantifie = Vertex(vertex.index, verticesQuantifiePosition.copy(), vertex.neighbors)
            self.vertices[vertex.index].position = verticesQuantifiePosition.copy()
            quantifiedVertices[l] = vertexQuantifie
            l += 1
        return quantifiedVertices

    def quantifyNormals(self, pointNormalizeNormals, coefficient):
        quantifiedNormals = len(pointNormalizeNormals) * [None]
        l = 0
        for vertex in pointNormalizeNormals:
            verticesQuantifieNormals = []
            for i in range(3):
                # print(vertex.normal)
                verticesQuantifieNormals.append(round(vertex.normal[i] * coefficient))
            normalsQuantifie = Vertex(vertex.index, vertex.position, vertex.neighbors,
                                      normal=verticesQuantifieNormals.copy())
            quantifiedNormals[l] = normalsQuantifie
            l += 1
        return quantifiedNormals

    def quantification(self,precision):
        minVertices, maxVertices = self.getBoundingBoxVertices()
        file = open(self.filename, "a")
        file.write("BBvMin" + str(minVertices) + "\n")
        file.write("BBvMax" + str(maxVertices) + "\n")

        normalizePointVertices = self.remapingVertices(minVertices, maxVertices)
        quantifiedVertices = self.quantifyVertices(normalizePointVertices, precision)


        minNormals, maxNormals = self.getBoundingBoxNormals()
        file.write("BBnMin" + str(minNormals) + "\n")
        file.write("BBnMax" + str(maxNormals) + "\n")
        normalizePointNormals = self.remapingNormals(minNormals, maxNormals)
        quantifiedNormals = self.quantifyNormals(normalizePointNormals, precision)
        file.close()
        return quantifiedVertices, quantifiedNormals
        # verticeDequantifie = self.dequantificationVertices(quantifiedVertices, precision)
        # reconstructVertices = self.remapingInv(verticeDequantifie, minVertice, maxVertice)
        # Parser.writeMesh(quantifiedVertices, self.triangles, filenameMeshQuantify)



# def compressWithHuffman(filenameMeshQuantify, filenameCompressHuffman):
#     fileQuantifie = open(filenameMeshQuantify, 'r')
#     text = fileQuantifie.read()
#     textCompresser, dico = huffman.compresser(text)
#     print("Avant : {} bits / Après : {} bits".format(len(text), len(textCompresser)))
#     fileCompress = open(filenameCompressHuffman, "w")
#     fileCompress.write(textCompresser)
#     fileCompress.close()
#     fileUncompress = open(filenameCompressHuffman, "r")
#
#
# def uncompressWithHuffman(filenameCompressHuffman):
#     fileUncompress = open(filenameCompressHuffman, "r")
#     filenameUncompressHuffman = fileUncompress.read()


# r = v + u - w
def prediction(vPosition, uPosition, wPosition):
    rPosition = []
    for i in range(0,3):
        rPosition.append(vPosition[i] + uPosition[i] - wPosition[i])
    return rPosition

def compressionMarkov(sourceFilename, destinationFilename):
    sourceFile = open(sourceFilename, 'rb')
    destinationFile = open(destinationFilename, 'wb')
    engine = Engine()
    engine.compress(sourceFile, destinationFile)
