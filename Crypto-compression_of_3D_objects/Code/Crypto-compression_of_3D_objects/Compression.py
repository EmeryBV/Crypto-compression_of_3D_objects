import random

import Parser
from Edge import Edge
from Vertex import Vertex
from ActiveList import ActiveList

import numpy as np
import decimal as dc


class Compression:

    def __init__(self, vertices, faces):
        self.stack = []
        self.vertices = vertices
        self.triangles = faces

    def getStartTriangle(self):
        return self.triangles[random.randint(0, len(self.triangles) - 1)]

    def encodeConnectivity(self, filename):
        file = open(filename, "w")
        start = self.getStartTriangle()
        startVertices = start.vertices

        AL = ActiveList(startVertices)

        # AL1 = ActiveList()
        self.encode(filename, "add", startVertices[0].valence)
        self.encode(filename, "add", startVertices[1].valence)
        self.encode(filename, "add", startVertices[2].valence)

        AL.focusVertex = startVertices[random.randint(0, 2)]

        # vertexFocus = startVertices[random.randint(0, 2)]
        # vertexFocus.setFocus(True)

        self.stack.append(AL)
        while self.stack:
            AL = self.stack.pop()
            while AL:
                u = AL.nextFreeEdge( self.vertices )
                # u = Vertex(0, 0)  # A MODIFIER
                if not AL.contains(u):
                    print(u.position)
                    AL.add(u)
                    self.encode(filename, "add", str(u.valence))
                    print("add" +str(u.valence))
                    # encodedeGeometry(AL)
                    u.encode()
                else :
                    if AL.contains(u):
                        self.stack.append(AL.split(u))
                        self.encode(filename, "split", str(AL.getOffset(u)))
                        print("split" + str(AL.getOffset(u)))
                    else:
                        for i in range(len(self.stack)):
                            if self.stack[i].contains(u):
                                AL.merge(self.stack[i], u)
                                self.stack.remove(i)
                                self.encode(filename, "merge", str(i), str(AL.getOffset(u)))
                AL.removeFullVertices(self.vertices)
                if AL.focusVertex.isFull(self.vertices):
                    for vertexNeighbor in range(len(AL.focusVertex.neighbors)):

                        if not vertexNeighbor.isFull(self.vertices):
                            AL.focusVertex = vertexNeighbor

    def encodeGeometry(self, AL):

        vertex = AL[len(AL) - 1]
        predictVertex = prediction(AL[0].position, AL[len(AL) - 2].position, AL[len(AL) - 3].position)
        # print(vertex.position)
        # print(predictVertex)
        result = vertex.position - predictVertex
        # print(result)
        # print("\n")

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
            newVertex = Vertex(vertex.index, normalizeVertex.copy(), vertex.neighbors)
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

    def quantifieVertices(self, pointNormalize, coefficient):
        verticeQuantifie = len(pointNormalize) * [None]
        l = 0
        for vertex in pointNormalize:
            verticesQuantifiePosition = []
            for i in range(3):
                verticesQuantifiePosition.append(round(vertex.position[i] * coefficient))

            # print(verticesQuantifiePosition)
            vertexQuantifie = Vertex(vertex.index, verticesQuantifiePosition.copy(), vertex.neighbors)
            verticeQuantifie[l] = vertexQuantifie
            # print(verticeQuantifie[l].position)
            l += 1
        return verticeQuantifie

    def dequantificationVertices(self, verticeQuantifie, coefficient):
        verticeDequantifie = len(verticeQuantifie) * [None]
        l = 0
        for vertex in verticeQuantifie:
            verticesDequantifiePosition = []
            for i in range(3):
                verticesDequantifiePosition.append(round(vertex.position[i] / coefficient))
            # print(verticesQuantifiePosition)
            vertexdeQuantifie = Vertex(vertex.index, verticesDequantifiePosition.copy(), vertex.neighbors)
            verticeDequantifie[l] = vertexdeQuantifie
            # print(verticeQuantifie[l].position)
            l += 1
        return verticeDequantifie

    def quantification(self, precision):
        minVertice, maxVertice = self.getBoundingBox()
        normalizePoint = self.remaping(minVertice, maxVertice)
        verticeQuantifie = self.quantifieVertices(normalizePoint, precision)
        verticeDequantifie = self.quantifieVertices(verticeQuantifie, precision)
        reconstructVertices = self.remapingInv(verticeDequantifie, minVertice, maxVertice)
        Parser.writeMesh(reconstructVertices, self.triangles)

    def encode(self, filename, instruction, valence=None, offset=None, index=None):
        file = open(filename, "w")

        if instruction == "add":
            line = " ".join([instruction, str(valence)])
        elif instruction == "split":
            line = " ".join([instruction, str(offset)])
        else:
            line = " ".join([instruction, str(index), str(offset)])

        file.write(line + "\n")

def isFull(self):
    for n in self.neighbors:
        if not n.isEncoded():
            return False
    return True
# r = v + u - w
def prediction(vPosition, uPosition, wPosition):
    rPosition = vPosition + uPosition - wPosition
    return rPosition

