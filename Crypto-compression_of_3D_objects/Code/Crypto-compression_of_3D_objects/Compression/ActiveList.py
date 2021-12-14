class ActiveList:

    def __init__(self, vertexList):
        self.vertexList = vertexList
        self.focusVertex = None

    def addVertex(self, vertex):
        self.vertexList.append(vertex)

    def contains(self, vertex):
        return vertex in self.vertexList

    def empty(self):
        return len(self.vertexList) == 0

    def split(self, vertex):
        ALBis = []

        for i in range( len(self.vertexList)-1, -1, -1):
            if vertex == self.vertexList[i]:
                ALBis = ActiveList(self.vertexList[0:i + 1])
                self.vertexList = self.vertexList[i:]
                break



        return ALBis

    def splitDecompression(self, offset ):
        splitVertex = self.vertexList[offset]
        ALBis = ActiveList( self.vertexList[offset:])
        self.vertexList = self.vertexList[0:offset + 1]
        return ALBis, splitVertex

    def mergeDecompression(self, AList, offset):
        self.vertexList = self.vertexList + AList.vertexList[offset:] + AList.vertexList[0:offset]
        print("Vertex in AL Merge =", [n.index for n in self.vertexList])

    def getOffset(self, vertex):
        result = 0
        copy = self.vertexList.copy()
        copy.reverse()
        for v in copy:
            if vertex.index != v.index:
                result += 1
            else:
                break

        return result

    def nextFocus(self):
        self.focusVertex = self.vertexList[0]

    def merge(self, AL1, vertex):
        for i in range(len(AL1.vertexList)):
            if AL1.vertexList[i] == vertex:
                self.vertexList = self.vertexList + AL1.vertexList[i:] + AL1.vertexList[0:i+1]
                break
        print("Vertex in AL Merge =", [n.index for n in self.vertexList])

    def removeFullVertices(self, triangles):
        print("\n")
        bool = False

        for vertex in self.vertexList[:]:
            if vertex.isFull():
                bool = True
                print("deleting : ", vertex.index)
                if len(self.vertexList) > 2:
                    if vertex == self.focusVertex:
                        self.encodeFace(self.focusVertex, self.vertexList[1], self.vertexList[len(self.vertexList) - 1], triangles)
                    else:
                        if vertex == self.vertexList[len(self.vertexList) - 1]:
                            self.encodeFace(self.vertexList[0], self.vertexList[len(self.vertexList) - 2], vertex, triangles)
                        else:
                            index = self.vertexList.index( vertex )
                            self.encodeFace( self.vertexList[index - 1], self.vertexList[index],self.vertexList[index + 1], triangles )
                    print("deleting vertex ", vertex.index )
                self.vertexList.remove(vertex)
        return bool

    def encodeFace(self, v1, v2, v3, triangles ):
        face = self.getFaces(v1, v2, v3, triangles)
        if not face:
            return
        for edge in face.edges:
            if not edge.isEncoded():
                print("encode", edge.vertices)
                edge.encode()

    def getFaces(self, v1, v2, v3, triangles):
        for face in triangles:
            if v1 != v2 and v1 != v3 and v2 != v3 and face.composedOf(v1, v2, v3):
                print( v1.index, v2.index, v3.index)
                print( [ e.vertices for e in  face.edges ]  )
                return face
        print( "No face found between" ,v1.index, v2.index, v3.index)
        return None

    def sortFocusVertexNeighbors(self, allVertices, allTriangles ):
        predecessor = self.vertexList[ len(self.vertexList) -1 ]
        for i in range(0, len(self.focusVertex.neighbors ) ):
            neighbor = allVertices[ self.focusVertex.neighbors[i] ]
            if neighbor == predecessor:
                self.focusVertex.neighbors = self.focusVertex.neighbors[i:] + self.focusVertex.neighbors[0:i]
                self.focusVertex.edges = self.focusVertex.edges[i:] + self.focusVertex.edges[0:i]

        print( "Before sort ", self.focusVertex.neighbors)
        print( "Before sort ", [[e.vertices, e.isEncoded()] for e in self.focusVertex.edges])

        for i in range(0, len( self.focusVertex.neighbors ) ):
            neighbor = allVertices[ self.focusVertex.neighbors[i] ]
            if self.getFaces( self.focusVertex, neighbor, predecessor, allTriangles ) :
                self.focusVertex.neighbors = self.focusVertex.neighbors[i:] + self.focusVertex.neighbors[0:i]
                self.focusVertex.edges = self.focusVertex.edges[i:] + self.focusVertex.edges[0:i]
                break

        print( "After sort ", self.focusVertex.neighbors)
        print( "After sort ",  [[e.vertices, e.isEncoded()] for e in self.focusVertex.edges])

    def nextFreeEdge(self):
        print("EDGE de focus = ", [[n.vertices, n.isEncoded()] for n in self.focusVertex.edges])
        for edge in self.focusVertex.edges:
            if not edge.isEncoded():
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

    def makeConnectivity(self, vertex, newVertex, append = True):
        newVertex.addNeighbors([vertex, self.vertexList[len(self.vertexList) - 1]])
        newVertex.addEdge([vertex, self.vertexList[len(self.vertexList) - 1]])

        vertex.addNeighbors([newVertex])
        vertex.addEdge([newVertex])
        print("edges ", [e.vertices for e in newVertex.edges])

        if append:
            self.vertexList.append(newVertex)

    def encodeFace2(self, v1, v2, v3):
        v1.addNeighbors([v2, v3])
        v1.addEdge([v2, v3])

        v2.addNeighbors([v3])
        v2.addEdge([v3])

        v1.getEdge( v1, v2 ).encode()
        v1.getEdge( v1, v3 ).encode()
        v2.getEdge( v2, v3 ).encode()

    def removeFullVerticesValence(self):
        bool = False
        for vertex in self.vertexList[:]:
            # print(len( vertex.edges ))
            if vertex.isValenceFull():
                bool = True
                if vertex == self.focusVertex:
                    self.encodeFace2( self.focusVertex, self.vertexList[1], self.vertexList[len(self.vertexList) - 1] )
                else:
                    if vertex == self.vertexList[len(self.vertexList) - 1]:
                        self.encodeFace2( self.vertexList[0],  self.vertexList[len(self.vertexList) - 1], self.vertexList[len(self.vertexList) - 2])

                    else:
                        index = self.vertexList.index(vertex)
                        self.encodeFace2( self.vertexList[index-1],  self.vertexList[index], self.vertexList[index+1])

                self.vertexList.remove(vertex)
                print( "deleting", vertex.index )
        return bool
