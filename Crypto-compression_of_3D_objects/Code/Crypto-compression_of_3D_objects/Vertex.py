from Edge import Edge


class Vertex:

    def __init__(self, index, position, neighbors, edges=None, valence=None, normal = None):
        if edges is None:
            edges = []
        self.index = index
        self.position = position
        self.neighbors = neighbors
        self.edges = edges

        if valence == None:
            self.valence = len(self.neighbors)
        else:
            self.valence = valence

        self.focusVertex = False
        self.encoded = False
        self.normal = normal

    def setFocus(self, state):
        self.focusVertex = state

    def encode(self):
        self.encoded = True

    def isEncoded(self):
        return self.encoded

    def isFull(self):
        for edge in self.edges:
            if not edge.isEncoded():
                return False
        return True

    def isValenceFull(self):
        if int(self.valence) == len(self.neighbors):
            return True
        return False

    def containEdge(self, v1, v2):
        for edge in self.edges:
            if v1.index in edge.vertices and v2.index in edge.vertices:
                return True
        return False

    def getEdge(self, v1, v2):
        for edge in self.edges:
            if v1.index in edge.vertices and v2.index in edge.vertices:
                return edge
        return None

    def haveOneFreeEdge(self):
        # print(int(self.valence) )
        # print(len(self.neighbors)+1 )
        if int(self.valence) == len(self.neighbors) + 1:
            return True
        return False

    def addNeighbors(self, vertexList):
        for vertexNei in vertexList:
            if vertexNei not in self.neighbors:
                self.neighbors.append(vertexNei)
                vertexNei.neighbors.append(self)

    def addEdge(self, vertexList):
        for vertex in vertexList:
            containEdge = False
            for edge in self.edges:
                if vertex.index in edge.vertices:
                    # print("Erreur lors de l'insertion du vertex " + str(vertex.index)
                    #       + ", ce vertex est déjà présent dans une arrête")
                    containEdge = True
                    break
            if not containEdge:
                self.edges.append(Edge([self.index, vertex.index]))
                vertex.edges.append(Edge([vertex.index, self.index]))
