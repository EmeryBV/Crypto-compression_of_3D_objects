import random

import Parser
from Edge import Edge
from Face import Face
from Vertex import Vertex
from ActiveList import ActiveList
import re
import numpy as np
import decimal as dc


class Decompression:

    def __init__(self, filename):
        self.stack = []
        self.vertices = []
        self.triangles = []
        self.filename = filename

    def initFirstTriangle(self, v1, v2, v3):

        v1.addNeighbors([v2, v3])
        v2.addNeighbors([v3])

        v1.addEdge([v2, v3])
        v2.addEdge([v3])

    def decodeConnectivity(self):
        file = open(self.filename, 'r')
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
            AL = self.stack.pop(len(self.stack) - 1)
            AL.focusVertex = vertex1

            while AL.vertexList or "order" not in command:

                print("command ", i + 1, " ", command)
                print("FOCUS VERTEX = ", AL.focusVertex.index, AL.focusVertex.valence, len(AL.focusVertex.edges))
                if "add" in command:
                    print("AJOUT DE " + str(i))
                    print("ACTIVE LIST", [n.index for n in AL.vertexList])

                    newVertex = Vertex(i, position=[], neighbors=[], edges=[], valence=convertToInt(command))
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
                    print([o.index for o in AL.vertexList])

                    ALBis, splitVertex = AL.splitDecompression(convertToInt(command))
                    print("Split vertex : ", str(splitVertex.index))
                    AL.makeConnectivity(AL.focusVertex, splitVertex, append = False )  # connect previous focus with splitvertex
                    AL.nextFocus()
                    print("FOCUS: Voisin= ", [n.index for n in AL.focusVertex.neighbors])
                    print("FOCUS: Edge  = ", [n.vertices for n in AL.focusVertex.edges])
                    print("Split : ", str(convertToInt(command)), [o.index for o in AL.vertexList],
                          [o.index for o in ALBis.vertexList])

                    self.stack.append(ALBis)
                    for l in self.stack:
                        print( "AL in stack : ",  [ v.index for v in l.vertexList] )

                    if "order" not in command:
                        command = file.readline()

                while AL.removeFullVerticesValence():
                    pass

                print("AL : ", [o.index for o in AL.vertexList])
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

        self.decodeGeometry(file)

        self.orderVerticeList()
        self.makeTriangle()
        self.writeDecompressFile("decompressedMesh.obj")

    def makeTriangle(self):
        for vertex in self.vertices:
            for vertexNeigh in vertex.neighbors:
                for vertex1Neighbors in vertexNeigh.neighbors:

                    if vertex1Neighbors in vertexNeigh.neighbors and vertex1Neighbors in vertex.neighbors:

                        triangle = [vertex, vertex1Neighbors, vertexNeigh]
                        if not self.alreadyContainTriangle(triangle):
                            self.triangles.append(Face(triangle))

    def decodeGeometry(self, file):

        command = file.readline()
        index = 0

        while ("v" in command):
            self.associateCorrectCoord(command, index)
            command = file.readline()
            index += 1

        index = 0
        while ("n" in command):
            self.associateCorrectNormal(command, index)
            command = file.readline()
            index += 1

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

    def associateCorrectCoord(self, command, index):
        coordList = convertToListInt(command)
        for vertex in self.vertices:
            if vertex.index == index:
                vertex.position = coordList

    def associateCorrectNormal(self, command, index):
        coordList = convertToListInt(command)
        for vertex in self.vertices:
            # print(index)
            if vertex.index == index:
                vertex.normal = coordList

    def writeDecompressFile(self, filename):
        Parser.writeMesh(self.vertices, self.triangles, filename)

    # def repairMesh(self):
    #     for triangle in self.triangles:


def convertToInt(instruction):
    return int(re.findall(r"[-+]?\d*\.\d+|\d+", instruction)[0])


def convertToListInt(instruction):
    return re.findall(r"[-+]?\d*\.*\d+", instruction)
