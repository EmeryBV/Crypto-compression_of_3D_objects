import Compression
import sys

from Parser import readMesh
from Compression import Compression


def create_compress_file(filename):
    file = open(filename ,"x")
    return file

if __name__ == '__main__':
    filename = "compressMesh"
    file = create_compress_file(filename)
    file.write("test")
    meshFile = "./Mesh/OBJ/simpleShape.obj"
    vertices, faces = readMesh(meshFile)
    compression = Compression( vertices, faces)
    compression.EncodeConnectivity(filename)


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
