class ActiveList:

    def __init__(self):
        self.vertexList = []
        self.focusVertex = 0

    def add(self, vertex):
        self.vertexList.append(self, vertex)

    def isIn(self, vertex):
        return  vertex in self.vertexList