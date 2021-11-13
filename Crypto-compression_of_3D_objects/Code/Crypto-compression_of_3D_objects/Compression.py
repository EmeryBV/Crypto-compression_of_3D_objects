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

        AL = ActiveList(start)
        # AL1 = ActiveList()
        start[0].encode(filename, "add")
        start[1].encode(filename, "add")
        start[2].encode(filename, "add")

        vertexFocus = start[0]
        vertexFocus.setFocus(True)

        self.stack.append(AL)
        while (self.stack):
            AL = np.stack.pop()
            while (AL):
                u = vertexFocus.nextFreeEdge()  # A MODIFIER
                # u = Vertex(0, 0)  # A MODIFIER
                if u.isEncoded():
                    AL.add(u)
                    Vertex.encode(filename, "add", str("u.degree"))
                    u.encode()
                elif AL.contains(u):
                    self.stack.append(AL.split(u))
                    Vertex.encode("split", str(AL.getOffset(u)))
                else:
                    for i in range(len(self.stack)):
                        if self.stack[i].contains(u):
                            AL.merge(self.stack[i], u)
                            self.stack.remove(i)
                            Vertex.encode(filename, "merge", str(i) + " " + str(AL.getOffset(u)))
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
