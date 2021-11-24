class Face:

    def __init__(self, vertices, edges):
        self.vertices = vertices
        self.edges = edges
        pass

    def composedOf(self, v1, v2, v3):
        if v1 in self.vertices and v2 in self.vertices and v3 in self.vertices:

            return True
        return False
