from ActiveList import ActiveList
from numpy import  *

from Edge import Edge
from Vertex import Vertex


class Compression:

    def __init__(self):
        self.list_activeList = []

    def EncoreConnectivity(self,filename):
        file = open(filename, "x")
        stack = []
        AL = ActiveList()
        AL1 = ActiveList()
        while 1:
            # TODO: Selection d'un triangle aléatoire non visité
            file.write("add " + str(1))
            file.write("add " + str(2))
            file.write("add " + str(3))
            # TODO: Mettre le vertex 1 en focus
            stack.append(AL)
            while(stack):
                AL = stack.pop()
                while(AL):
                    # TODO: assigner à la variable e la prochaine arrete libre (nextFreeEdge() )
                    e = Edge() #A MODIFIER
                    # TODO: assigner à la variable u le vertice assigné à la variable e (neighboringVertex() )
                    u=Vertex(0,0) #A MODIFIER
                    if(u.isEncoded()):
                        AL.add(u)
                        file.write("add " + str("u.degree"))
                        u.encode()
                    else:
                        if AL.contains(u):
                            stack.append(AL.split(e))
                            file.write("split " + str("offset of u since pivot"))
                        else:
                            for i in range(len(self.list_activeList)):
                                print("")
                                #???



    def encodeGeometry(self):
        print("")

    def quantification(self, listVertex):
        print("")

    # r = v + u - w
    def prediction(self, vPosition, uPosition, wPosition):
        rPosition = vPosition + uPosition - wPosition
        return rPosition
