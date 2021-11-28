class ActiveList:

    def __init__(self, vertexList):
        self.vertexList = vertexList
        self.focusVertex = None

    def addVertex(self, vertex):
        self.vertexList.append(vertex)

    def contains(self, vertex):
        return vertex in self.vertexList

    def empty(self):
        return len(self.vertexList) == 0

    def split(self, vertex):
        ALBis = None
        for i in range(0, len(self.vertexList)):
            if vertex == self.vertexList[i]:
                ALBis = ActiveList(self.vertexList[0:i + 1])
                self.vertexList = self.vertexList[i:]
                break

        temp = self.vertexList
        if len(self.vertexList) < len(ALBis.vertexList):
            self.vertexList = ALBis.vertexList
            ALBis.vertexList = temp

        return ALBis

    def getOffset(self, vertex):
        result = 0
        copy = self.vertexList.copy()
        copy.reverse()
        for v in copy:
            if self.focusVertex.index != v.index:
                result += 1
            else:
                break

        return result

    def nextFocus(self):
        self.focusVertex = self.vertexList[0]

    def merge(self, AL1, vertex):
        for i in range(len(AL1.vertexList)):
            if AL1.vertexList[i] == vertex:
                for y in range(0, len(self.vertexList)):
                    AL1.vertexList.insert(i + y + 1, self.vertexList[
                        y])  # On ne veut pas copier 2 fois vertex dans la nouvelle liste
                break
        self.vertexList = AL1.vertexList
        print("Vertex in AL Merge =", [n.index for n in AL1.vertexList])

    def removeFullVertices(self):
        deleteVertices = []
        for vertex in self.vertexList:
            if vertex.isFull():
                print("Suppression de:", vertex.index)
                deleteVertices.append(vertex)
        for vertexDel in deleteVertices:
            self.vertexList.remove(vertexDel)
        return deleteVertices

    def removeFullVerticesValence(self):
        deleteVertices = []
        for vertex in self.vertexList:
            if vertex.isValenceFull():
                # print("index = " + str(vertex.index))
                print("Voisin= ", [n.index for n in vertex.neighbors])
                print("Suppression de:", vertex.index)
                deleteVertices.append(vertex)
        for vertexDel in deleteVertices:
            self.vertexList.remove(vertexDel)

    def sortFocusVertexNeighbors(self, allVertices ):
        predecessor = self.vertexList[ len(self.vertexList) -1 ]
        for i in range( len( self.focusVertex.neighbors ) ):
            neighbor = allVertices[ self.focusVertex.neighbors[i] ]
            if not neighbor.isEncoded() and neighbor.getEdge( neighbor, self.focusVertex ) and neighbor.getEdge( neighbor, predecessor ):
                self.focusVertex.neighbors = self.focusVertex.neighbors[i:] + self.focusVertex.neighbors[0:i]
                self.focusVertex.edges = self.focusVertex.edges[i:] + self.focusVertex.edges[0:i]
                break

    def nextFreeEdge(self):
        print("EDGE de focus = ", [n.vertices for n in self.focusVertex.edges])
        for edge in self.focusVertex.edges:
            if not edge.isEncoded():
                edge.encode()
                print("encode", edge.vertices)
                return edge

        print("nextFreeEdge return None")
        return None

    def vertexAlongEdge(self, edge):
        for vertex in edge.vertices:
            if vertex != self.focusVertex.index:
                return vertex

    def nextFreeVertex(self, verticesList):
        for n in self.focusVertex.neighbors:
            if not verticesList[n].isEncoded():
                return verticesList[n]
            else:
                print("Auncun vertex")
                return None

    def getPreviousNeighbour(self, vertex):
        for i in range(len(self.focusVertex.neighbors)):
            if self.focusVertex.neighbors[i] == vertex.index:
                return self.focusVertex.neighbors[i - 1]

    def nextfreeEdgeDecode(self):
        for vertex in self.vertexList:
            # print(vertex.index)
            # print(vertex.valence)
            # print("Edge= ", [n.index for n in vertex.neighbors])
            if int(vertex.valence) >= len(vertex.neighbors):
                return vertex
        print("No free Edge")

    def makeConnectivity(self, newVertex):
        newVertex.addNeighbors([self.focusVertex, self.vertexList[len(self.vertexList) - 1]])
        newVertex.addEdge([self.focusVertex, self.vertexList[len(self.vertexList) - 1]])
        # self.vertexList[len(self.vertexList) - 1].addNeighbors([newVertex])
        # self.vertexList[len(self.vertexList) - 1].addEdge([newVertex])

        self.focusVertex.addNeighbors([newVertex])
        self.focusVertex.addEdge([newVertex])

        self.joinNeigborsLink(newVertex)

        self.vertexList.append(newVertex)

    def twoVertexNotConnected(self, vertex, vertexText):
        listVertexFree = []

        cpt = 0
        for vertexNei in vertexText.neighbors:
            # print(vertex.index)
            # print(vertexNei.index)
            # print(self.focusVertex in vertexNei.neighbors)
            if vertex in vertexNei.neighbors:
                cpt += 1
        # print("cpt =" + str(cpt) )
        # print("\n")
        if cpt < 2:
            return True
        return False

    def joinNeigborsLink(self, newVertex):
        for neighborsVertex in self.focusVertex.neighbors:
            # print("index", neighborsVertex.index)
            # print("index", neighborsVertex.index)
            # print(" Voisin= ", [n.index for n in neighborsVertex.neighbors])
            # print(neighborsVertex.haveOneFreeEdge())
            # print(newVertex not in neighborsVertex.neighbors)
            # print(self.focusVertex.isValenceFull())
            # print("\n")
            if not neighborsVertex.isValenceFull() and self.twoVertexNotConnected(self.focusVertex,neighborsVertex) and newVertex not in neighborsVertex.neighbors \
                    and newVertex != neighborsVertex and self.focusVertex.isValenceFull():
                neighborsVertex.addNeighbors([newVertex])
                neighborsVertex.addEdge([newVertex])

    def joinFirstAndLastNeigbor(self, newVertex):
        newVertex.addNeighbors([self.focusVertex.neighbors[0]])
        newVertex.addEdge([self.focusVertex.neighbors[0]])
