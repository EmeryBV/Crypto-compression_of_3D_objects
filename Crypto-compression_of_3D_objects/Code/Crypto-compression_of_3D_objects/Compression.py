import random

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

    def EncodeConnectivity(self, filename):
        file = open(filename, "w")
        start = self.getStartTriangle()
        startVertices = start.vertices

        AL = ActiveList(start)
        # AL1 = ActiveList()
        self.encode(filename, "add", startVertices[0].valence)
        self.encode(filename, "add", startVertices[1].valence)
        self.encode(filename, "add", startVertices[2].valence)

        vertexFocus = startVertices[random.randint(0, 2)]
        vertexFocus.setFocus(True)

        self.stack.append(AL)
        while (self.stack):
            AL = self.stack.pop()
            while (AL):
                u = vertexFocus.nextFreeEdge()  # A MODIFIER
                # u = Vertex(0, 0)  # A MODIFIER
                if u.isEncoded():
                    AL.add(u)
                    self.encode(filename, "add", str(u.valence))
                    u.encode()
                elif AL.contains(u):
                    self.stack.append(AL.split(u))
                    self.encode(filename, "split", str(AL.getOffset(u)))
                else:
                    for i in range(len(self.stack)):
                        if self.stack[i].contains(u):
                            AL.merge(self.stack[i], u)
                            self.stack.remove(i)
                            self.encode(filename, "merge", str(i), str(AL.getOffset(u)))

                AL.removeFullVertices()
                if vertexFocus.isFull():
                    for vertexNeighbor in range(len(start[0].neighbors)):
                        if not vertexNeighbor.isFull():
                            vertexFocus = vertexNeighbor

    def encodeGeometry(self):
        print("")

    def quantification(self, listVertex, precision):
        dc.getcontext().prec = precision
        for i in range(len(listVertex)):
            listVertex[i] = dc.Decimal(listVertex[i])

    # r = v + u - w
    def prediction(self, vPosition, uPosition, wPosition):
        rPosition = vPosition + uPosition - wPosition
        return rPosition

    def encode(self, filename, instruction, valence=None, offset=None, index=None):
        file = open(filename, "w")

        if instruction == "add":
            line = " ".join([instruction, str(valence)])
        elif instruction == "split":
            line = " ".join([instruction, str(offset)])
        else:
            line = " ".join([instruction, str(index), str(offset)])

        file.write(line + "\n")
