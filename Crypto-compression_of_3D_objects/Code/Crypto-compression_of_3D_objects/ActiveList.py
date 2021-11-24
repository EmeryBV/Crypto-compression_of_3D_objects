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
                ALBis = ActiveList( self.vertexList[0:i+1] )
                self.vertexList = self.vertexList[i:]
                break

        temp = self.vertexList
        if len( self.vertexList ) < len( ALBis.vertexList ):
            self.vertexList  = ALBis.vertexList
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
                    AL1.vertexList.insert(i + y + 1, self.vertexList[y])  # On ne veut pas copier 2 fois vertex dans la nouvelle liste
                break
        print("Vertex in AL Merge =", [n.index for n in AL1.vertexList])

    def removeFullVertices(self):
        deleteVertices = []
        for vertex in self.vertexList:
            if vertex.isFull():
                self.vertexList.remove(vertex)
                print("Suppression de:", vertex.index)
                deleteVertices.append(vertex)
        return deleteVertices
        # self.focusVertex = self.vertexList[0]

    def nextFreeEdge(self):
        for edge in self.focusVertex.edges:
            if not edge.isEncoded():
                edge.encode()
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
                return self.focusVertex.neighbors[i-1]
