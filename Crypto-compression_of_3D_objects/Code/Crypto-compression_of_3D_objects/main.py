import sys

from Parser import readMesh
from Compression import Compression
from Decompression import Decompression


def create_compress_file(filename):
    file = open(filename, "w")
    return file

if __name__ == '__main__':
    filename = "compressedMesh.txt"
    file = create_compress_file(filename)
    # file.write("test.obj")
    # meshFile = "./Mesh/OBJ/cube.obj"
    meshFile = "./Mesh/OBJ/simpleShape.obj"
    # meshFile = "./Mesh/OBJ/cube.obj"
    # meshFile = "./Mesh/OBJ/monkey.obj"
    vertices, faces = readMesh(meshFile)
    # decompression = Decompression()
    compression = Compression(vertices, faces)
    compression.encodeConnectivity(filename)

    # compression.quantification(1024)

    # compression.remapingInv(normalizePont, minVertice, maxVertice)
    # AL = []
    # Parser.writeMesh(compression.vertices, compression.triangles)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
