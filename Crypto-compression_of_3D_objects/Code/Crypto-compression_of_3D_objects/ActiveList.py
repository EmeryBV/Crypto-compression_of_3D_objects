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
        ALBis = []
        for i in range(0, len(self.vertexList)):
            # print(self.vertexList[i].index)
            if vertex == self.vertexList[i]:
                ALBis = ActiveList(self.vertexList[i:])
                self.vertexList = self.vertexList[0:i + 1]
                break
        ALBis.focusVertex = ALBis.vertexList[0]
        AL = self
        if len(ALBis.vertexList) >= len(self.vertexList):
            AL = ALBis
            ALBis = self

        return AL, ALBis

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
        for i in range(len(AL1.vertexList)):
            if AL1.vertexList[i] == vertex:
                for y in range(0, len(self.vertexList)):
                    AL1.vertexList.insert(i + y + 1, self.vertexList[
                        y])  # On ne veut pas copier 2 fois vertex dans la nouvelle liste
                break
        print("Vertex in AL Merge =", [n.index for n in AL1.vertexList])

    def removeFullVertices(self):
        deleteVertices = []
        for vertex in self.vertexList:
            if vertex.isFull():
                self.vertexList.remove(vertex)
                print("Suppresion de:", vertex.index)
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
