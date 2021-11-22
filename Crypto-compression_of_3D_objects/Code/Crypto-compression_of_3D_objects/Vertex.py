class Vertex:

    def __init__(self, index, position, neighbors ,edges = None):
        self.index = index
        self.position = position
        self.neighbors = neighbors
        self.edges  = edges
        self.valence = len(self.neighbors)
        self.focusVertex = False
        self.encoded = False

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

    # def neighboringVertex(self,edge):
