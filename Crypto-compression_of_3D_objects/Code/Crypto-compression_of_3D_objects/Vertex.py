class Vertex:

    def __init__(self, position, degree):
        self.position = position
        self.neighbors = neighbors
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
        for n in self.neighbors:
            if not n.isEncoded():
                return False
        return True

    def nextFreeEdge(self):
        for n in self.neighbors:
            if not n.isEncoded():
                return n

    # def neighboringVertex(self,edge):
