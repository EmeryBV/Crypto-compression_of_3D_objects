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
    meshFile = "./Mesh/OBJ/cube.obj"
    vertices, faces = readMesh(meshFile)
    # decompression = Decompression()

    compression = Compression( vertices, faces)
    print(faces[0].vertices)
    # compression.quantification(2)
    AL = []
    AL.append(vertices[0])
    AL.append(vertices[3])
    AL.append(vertices[7])
    AL.append(vertices[4])
    compression.encodeGeometry(AL)
    # compression.EncodeConnectivity(filename)


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
