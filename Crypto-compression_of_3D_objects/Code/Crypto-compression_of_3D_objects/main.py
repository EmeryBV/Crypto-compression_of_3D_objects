import sys
import huffman

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
    meshFile = "./Mesh/OBJ/cube.obj"
    # meshFile = "./Mesh/OBJ/simpleSphere.obj"
    vertices, faces = readMesh(meshFile)
    # decompression = Decompression()
    compression = Compression(vertices, faces)
    # print(faces[0].vertices)
    # compression.quantification(20)
    compression.encodeConnectivity(filename)
    quantifyMesh = "quantifyMesh.obj"
    compressMeshHuffman = "meshCompressHuffman.txt"
    # compression.quantification(256, quantifyMesh,compressMeshHuffman)

    # print(textUncompress)

    # print(TextConvertToString)
    # textDecompresser = huffman.decompresser(textCompresser, dico)

    # print(textDecompresser)
    # compression.remapingInv(normalizePont, minVertice, maxVertice)
    # AL = []
    # Parser.writeMesh(compression.vertices, compression.triangles)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
