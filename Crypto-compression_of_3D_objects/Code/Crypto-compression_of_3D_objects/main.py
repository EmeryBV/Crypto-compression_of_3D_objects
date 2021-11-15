import sys

from Parser import readMesh
from Compression import Compression


def create_compress_file(filename):
    file = open(filename ,"w")
    return file

if __name__ == '__main__':
    filename = "compressedMesh.obj"
    file = create_compress_file(filename)
    file.write("test")
    meshFile = "./Mesh/OBJ/simpleShape.obj"
    vertices, faces = readMesh(meshFile)
    decompression = Decompression()
    # compression = Compression( vertices, faces)
    # compression.EncodeConnectivity(filename)


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
