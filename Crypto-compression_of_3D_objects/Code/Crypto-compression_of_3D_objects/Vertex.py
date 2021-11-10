class Vertex:

    def __init__(self, position, degree):
        self.position = position
        self.degre = degree
        self.focusVertex = False
        self.encoded = False
        self.neighbors = []

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

