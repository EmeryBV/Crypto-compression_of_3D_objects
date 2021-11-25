import random

import Parser
from Edge import Edge
from Vertex import Vertex
from ActiveList import ActiveList
import huffman
import binary_operation
import numpy as np
import decimal as dc


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

        AL.focusVertex = startVertices[0]
        # vertexFocus = startVertices[random.randint(0, 2)]
        # vertexFocus.setFocus(True)

        self.stack.append(AL)

        while self.stack:
            AL = self.stack.pop(len(self.stack) - 1)

            while AL.vertexList:
                print("FOCUS VERTEX = ", AL.focusVertex.index)
                print("Vertex in AL = ", [n.index for n in AL.vertexList])
                print("NEIGHBORS = ", [n for n in AL.focusVertex.neighbors])

                e = AL.nextFreeEdge()
                u = self.vertices[AL.vertexAlongEdge(e)]

                print("Neighbor vertex u = ", u.index)
                # print("Valence u=", u.valence)
                if not u.isEncoded():
                    for v3 in AL.vertexList:
                        self.encodeFace(u, AL.focusVertex, v3)
                    self.encodeVertexInFile("add", vertex=u, valence=str(u.valence))
                    AL.addVertex(u)
                    traversalOrder.append(u.index)
                    # encodedeGeometry(AL)

                elif AL.contains(u):
                    # ALBis = AL.split(u)
                    print("Split occuring on ", u.index)
                    # print("AL : ", [k.index for k in AL.vertexList], "ALBis : ", [k.index for k in ALBis.vertexList])
                    # self.stack.append(ALBis)
                    # self.encodeVertexInFile("split", vertex=u, offset=str(AL.getOffset(u)))
                    # # print("Vertex in ALBIS =", [n.index for n in ALBis.vertexList])
                else:
                    for AList in self.stack:
                        if AList.contains(u):
                            print("Vertex where u is found ", [n.index for n in AList.vertexList])
                            self.encodeVertexInFile("merge", vertex=u, index=u.index,
                                                    offset=str(AL.getOffset(u)))
                            AL.merge(AList, u)
                            # AL = AList
                            self.stack.remove(AList)
                            break
                AL.removeFullVertices()
                for AL2 in self.stack:
                    AL2.removeFullVertices()
                # print(AL.vertexList)
                if AL.vertexList and AL.focusVertex.isFull():
                    AL.nextFocus()
        print(traversalOrder)
        line = ""
        for index in traversalOrder:
            line += "".join(str(index)) + " "
        file = open(self.filename, "a")
        file.write("order "+line + "\n")
        file.close()


    def encodeGeometry(self, AL):

        vertex = AL[len(AL) - 1]
        predictVertex = prediction(AL[0].position, AL[len(AL) - 2].position, AL[len(AL) - 3].position)
        # print(vertex.position)
        # print(predictVertex)
        result = vertex.position - predictVertex
        # print(result)
        # print("\n")

    def encodeFace(self, v1, v2, v3):
        face = self.getFaces(v1, v2, v3)
        if face is not None and v1 != v2 and v2 != v3 and v1 != v3:
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

    def getBoundingBox(self):
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

    def getFaces(self, v1, v2, v3):
        for face in self.triangles:
            if face.composedOf(v1, v2, v3):
                return face

    def remaping(self, minVertice, maxVertice):
        pointNormalize = (len(self.vertices)) * [None]
        sumExtremum = []
        for i in range(3):
            sumExtremum.append(abs(minVertice[i]) + abs(maxVertice[i]))
        l = 0
        for vertex in self.vertices:
            # print(vertex.position)
            normalizeVertex = []
            normalizeVertex.clear()
            for i in range(0, 3):
                normalizeVertex.append((vertex.position[i] + abs(minVertice[i])) / sumExtremum[i])
            # print(normalizeVertex)
            newVertex = 0
            newVertex = Vertex(vertex.index, normalizeVertex.copy(), vertex.neighbors, [])
            pointNormalize[l] = newVertex

            # print(pointNormalize[l].position)
            # print(pointNormalize)

            # print("\n")
            l += 1
        # print("\n")
        # print("aaa")

        return pointNormalize

    def remapingInv(self, pointNormalize, minVertice, maxVertice):
        vertexRemap = []
        l = 0
        for vertex in pointNormalize:
            vertexquantizePosition = []
            for i in range(3):
                vertexquantizePosition.append(
                    vertex.position[i] * (abs(minVertice[i]) + abs(maxVertice[i])) - abs(minVertice[i]))
            # print(normalizeVertex)
            vertexRemap.append(Vertex(vertex.index, vertexquantizePosition, vertex.neighbors))

            # print(vertexquantize[l].position)
            # print("\n")
            l += 1
        return vertexRemap

    def quantifyVertices(self, pointNormalize, coefficient):
        quantifiedVertices = len(pointNormalize) * [None]
        l = 0
        for vertex in pointNormalize:
            verticesQuantifiePosition = []
            for i in range(3):
                verticesQuantifiePosition.append(round(vertex.position[i] * coefficient))

            vertexQuantifie = Vertex(vertex.index, verticesQuantifiePosition.copy(), vertex.neighbors)

            quantifiedVertices[l] = vertexQuantifie
            l += 1
        return quantifiedVertices

    def dequantificationVertices(self, quantifiedVertices, coefficient):
        verticeDequantifie = len(quantifiedVertices) * [None]
        l = 0
        for vertex in quantifiedVertices:
            verticesDequantifiePosition = []
            for i in range(3):
                verticesDequantifiePosition.append(round(vertex.position[i] / coefficient))
            # print(verticesQuantifiePosition)
            vertexdeQuantifie = Vertex(vertex.index, verticesDequantifiePosition.copy(), vertex.neighbors)
            verticeDequantifie[l] = vertexdeQuantifie
            # print(quantifiedVertices[l].position)
            l += 1
        return verticeDequantifie

    def quantification(self, precision, filenameMeshQuantify, filenameCompressHuffman):
        minVertice, maxVertice = self.getBoundingBox()
        normalizePoint = self.remaping(minVertice, maxVertice)
        quantifiedVertices = self.quantifyVertices(normalizePoint, precision)
        verticeDequantifie = self.dequantificationVertices(quantifiedVertices, precision)
        reconstructVertices = self.remapingInv(verticeDequantifie, minVertice, maxVertice)
        Parser.writeMesh(quantifiedVertices, self.triangles, filenameMeshQuantify)
        compressWithHuffman(filenameMeshQuantify, filenameCompressHuffman)


def compressWithHuffman(filenameMeshQuantify, filenameCompressHuffman):
    fileQuantifie = open(filenameMeshQuantify, 'r')
    text = fileQuantifie.read()
    textCompresser, dico = huffman.compresser(text)
    print("Avant : {} bits / Après : {} bits".format(len(text) * 8, len(textCompresser)))
    fileCompress = open(filenameCompressHuffman, "w")
    fileCompress.write(textCompresser)
    fileCompress.close()
    fileUncompress = open(filenameCompressHuffman, "r")


def uncompressWithHuffman(filenameCompressHuffman):
    fileUncompress = open(filenameCompressHuffman, "r")
    filenameUncompressHuffman = fileUncompress.read()


# r = v + u - w
def prediction(vPosition, uPosition, wPosition):
    rPosition = vPosition + uPosition - wPosition
    return rPosition
