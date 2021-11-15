import random

from Edge import Edge
from Vertex import Vertex
from ActiveList import ActiveList

import numpy as np
import decimal as dc


class Decompression:

    def __init__(self):
        self.stack = []
        # self.vertices = vertices
        # self.triangles = faces


    def DecodeConnectivity(self, filename):
        file = open(filename,'w')
        AL = ActiveList()
        while True:
            line = file.readline()
            print(line)
            if ("" == line):
                print ("file finished")
                break

    def decode(self, filename, instruction, valence=None, offset=None, index=None):
        file = open(filename, "w")

        if instruction == "add":
            line = " ".join([instruction, str(valence)])
        elif instruction == "split":
            line = " ".join([instruction, str(offset)])
        else:
            line = " ".join([instruction, str(index), str(offset)])

        file.write(line + "\n")
