class Edge:

    def __init__(self, vertices ):
        self.vertices = vertices
        self.encoded = False

    def encode(self):
        self.encoded = True

    def isEncoded( self ):
        return self.encoded


