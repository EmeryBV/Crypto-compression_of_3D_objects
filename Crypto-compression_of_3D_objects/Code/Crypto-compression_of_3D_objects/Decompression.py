import random

from Edge import Edge
from Vertex import Vertex
from ActiveList import ActiveList
import re
import numpy as np
import decimal as dc


class Decompression:

    def __init__(self):
        self.stack = []
        self.vertices = []
        self.triangles = []

    def initFirstTriangle(self, v1, v2, v3):

        v1.addNeighbors([v2, v3])
        v2.addNeighbors([v3])

        v1.addEdge([v2, v3])
        v2.addEdge([v3])
    def decodeConnectivity(self, filename):
        file = open(filename, 'r')
        v1 = file.readline()
        v2 = file.readline()
        v3 = file.readline()

        vertex1 = Vertex(0, [], [], None, convertToInt(v1))
        vertex2 = Vertex(1, [], [], None, convertToInt(v2))
        vertex3 = Vertex(2, [], [], None, convertToInt(v3))
        self.initFirstTriangle(vertex1, vertex2, vertex3)
        AL = ActiveList([vertex1, vertex2, vertex3])
        self.vertices.extend([vertex1, vertex2, vertex3])
        self.stack.append(AL)
        i = 3
        emptyList = False
        while self.stack and not emptyList:
            AL = self.stack.pop(len(self.stack) - 1)
            while AL.vertexList:
                command = file.readline()
                if command == "":
                    emptyList = True
                print(command)
                AL.focusVertex = AL.nextfreeEdgeDecode()
                print("FOCUS VERTEX = ", AL.focusVertex.index)
                if not emptyList:
                    if "add" in command:
                        print("AJOUT DE " + str(i))
                        newVertex = Vertex(i, [], [], [], convertToInt(command))
                        AL.makeConnectivity(newVertex)
                        self.vertices.append(newVertex)
                        print("FOCUS: Voisin= ", [n.index for n in AL.focusVertex.neighbors])
                        print("FOCUS:Edge= ", [n.vertices for n in AL.focusVertex.edges])
                        print("newVertex: Voisin= ", [n.index for n in newVertex.neighbors])
                        print("newVertex:Edge= ", [n.vertices for n in newVertex.edges])
                        print('\n')
                        i += 1

                    for vertex in self.vertices:
                        if vertex.isValenceFull():
                            valenceFocusVertex = int(vertex.valence)
                            for k in range(1,valenceFocusVertex):

                                if not vertex.neighbors[k-1].containEdge(vertex.neighbors[k-1],vertex.neighbors[k]
                                                                                 ) and not vertex.neighbors[k-1].isValenceFull() and not vertex.neighbors[k].isValenceFull():

                                    vertex.neighbors[k - 1].addNeighbors([vertex.neighbors[k]])
                                    vertex.neighbors[k - 1].addEdge([vertex.neighbors[k]])
                                # if k==valenceFocusVertex and not vertex.neighbors[k].isValenceFull() and not vertex.neighbors[0].isValenceFull():
                                #     if not vertex.neighbors[k].containEdge(vertex.neighbors[k],  vertex.neighbors[0]):
                                #         print("Je rentre dans la boucle")
                                #         vertex.neighbors[k].addNeighbors([vertex.neighbors[0]])
                                #         vertex.neighbors[k].addEdge([vertex.neighbors[0]])

                AL.removeFullVerticesValence()
            command = file.readline()
            if ("order" in command):
                traverselOrder = convertToListInt(command)

                for i in range(len(traverselOrder)):
                    self.vertices[i].index = traverselOrder[i]

            for k in range(len(self.vertices)):
                print("index = " + str(self.vertices[k].index))
                print("Voisin= ", [n.index for n in self.vertices[k].neighbors])
                print("Edge= ", [n.vertices for n in self.vertices[k].edges])
                print("\n")

    def decode(self, filename, instruction, valence=None, offset=None, index=None):
        file = open(filename, "w")

        if instruction == "add":
            line = " ".join([instruction, str(valence)])
        elif instruction == "split":
            line = " ".join([instruction, str(offset)])
        else:
            line = " ".join([instruction, str(index), str(offset)])

        file.write(line + "\n")


def convertToInt(instruction):
    return re.findall(r'\d', instruction)[0]

def convertToListInt(instruction):
    return re.findall(r'\d', instruction)