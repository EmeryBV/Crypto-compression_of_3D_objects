class ActiveList:

    def __init__(self):
        self.vertexList = []
        self.focusVertex = 0

    def add(self, vertex):
        self.vertexList.append(self, vertex)

    def contains(self, vertex):
        return vertex in self.vertexList

    def empty(self):
        return len(self.vertexList) == 0

    def split(self, edge):
        AL1 = []
        AL1.append(edge)

    def merge(self, AL1, vertex):
        self.vertexList += AL1

    def removeFullVertices(self):
        self.vertexList.clear()