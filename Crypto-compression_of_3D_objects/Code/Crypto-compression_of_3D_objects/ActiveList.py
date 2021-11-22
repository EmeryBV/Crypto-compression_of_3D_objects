class ActiveList:

    def __init__(self, vertexList):
        self.vertexList = vertexList
        self.focusVertex = None

    def add(self, vertex):
        self.vertexList.append( vertex)

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
        vertexOffset = self.vertexList[len(self.vertexList )-1]
        i = 1
        while vertex.index != vertexOffset.index:
            i += 1
            result += 1
            vertexOffset = self.vertexList[len(self.vertexList - i)]
        return result

    def merge(self, AL1, vertex):
        self.vertexList += AL1

    def removeFullVertices(self, verticesList):
        for vertex in self.vertexList:
            if vertex.isFull(verticesList):
                self.vertexList.remove(vertex)
        self.focusVertex = self.vertexList[0]

    def nextFreeEdge(self, verticesList):
        for n in self.focusVertex.neighbors:
            if not verticesList[n].isEncoded():
                return verticesList[n]