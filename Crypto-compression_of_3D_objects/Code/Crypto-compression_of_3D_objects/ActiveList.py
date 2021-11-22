class ActiveList:

    def __init__(self, vertexList):
        self.vertexList = vertexList
        self.focusVertex = None

    def add(self, vertex):
        self.vertexList.append(vertex)

    def contains(self, vertex):
        return vertex in self.vertexList

    def empty(self):
        return len(self.vertexList) == 0

    def split(self, vertex):
        for i in range(0, len(self.vertexList)):
            if vertex == self.vertexList[i]:
                ALBis = ActiveList(self.vertexList[i:])
                self.vertexList = self.vertexList[0:i + 1]
                break

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

    def merge(self, AL1, vertex):
        self.vertexList += AL1

    def removeFullVertices(self, verticesList):
        for vertex in self.vertexList:
            if vertex.isFull():
                self.vertexList.remove(vertex)
        self.focusVertex = self.vertexList[0]

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
