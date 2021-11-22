class Vertex:

    def __init__(self, index, position, neighbors):
        self.index = index
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

    def isFull(self, verticesList):
        for n in self.neighbors:

            if not verticesList[n].isEncoded():
                return False
        return True


    # def neighboringVertex(self,edge):
