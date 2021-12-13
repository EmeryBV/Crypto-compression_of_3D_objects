from Parser import readMesh,readMeshBis
from Compression import Compression, Decompression
from Evaluation import compressionEvaluation
import copy

def create_compress_file(filename):
    file = open(filename, "w")
    return file


if __name__ == '__main__':
    compressedMesh = "results/compressedMesh.txt"
    compressedMeshHuffman = "results/compressedMeshHuffman.txt"
    decompressedMeshHuffman = "results/DecompressedMeshHuffman"

    decompressedMesh = "results/DecompressedMesh.obj"

    compressedMeshwithoutConnectivty = "results/withoutConnectivity/compressedMesh.obj"
    compressedMeshHuffmanWithoutConnectivity = "results/withoutConnectivity/compressedMeshHuffman.txt"
    decompressedMeshHuffmanWithoutConnectivity = "results/withoutConnectivity/DecompressedMeshMarkov.obj"
    decompressedMeshWithoutConnectivity = "results/withoutConnectivity/DecompressedMesh.obj"


    file = create_compress_file(compressedMesh)
    # file.write("test.obj")
    meshFile = "./Mesh/OBJ/sphereSub4.obj"
    seed = 2563
    quantification = 8
    vertices, faces = readMesh(meshFile)
    originalMesh = Compression.Compression(vertices, faces, compressedMesh)
    compression = copy.deepcopy(originalMesh)

    print("//////////////////////COMPRESSION//////////////////////")
    # compression.encodeConnectivity()
    # keyXOR, keyShuffling = compression.encodeGeometrySinceConnectivity(seed, quantification)
    # Compression.compressionHuffman(compressedMesh, compressedMeshHuffman)

    keyXOR, keyShuffling = compression.encodeGeometryWithoutConnectivity(seed, quantification, compressedMeshwithoutConnectivty)
    Compression.compressionHuffman(compressedMeshwithoutConnectivty, compressedMeshHuffmanWithoutConnectivity)


    print("//////////////////////DECOMPRESSION//////////////////////")
    # Decompression.decompressionHuffman(compressedMeshHuffman, decompressedMeshHuffman)
    # vertices, faces = readMesh(decompressedMeshHuffman)
    # decompression = Decompression.Decompression(decompressedMeshHuffman, decompressedMesh, keyXOR, keyShuffling)
    # decompression.decodeConnectivity()

    Decompression.decompressionHuffman(compressedMeshHuffmanWithoutConnectivity, decompressedMeshHuffmanWithoutConnectivity)
    print(decompressedMeshHuffmanWithoutConnectivity)
    vertices, faces = readMeshBis(decompressedMeshHuffmanWithoutConnectivity)
    decompression = Decompression.Decompression(decompressedMeshHuffmanWithoutConnectivity,
                                                decompressedMeshWithoutConnectivity, keyXOR, keyShuffling,vertices,faces)

    decompression.decodeGeometryNotSinceConnectivity()


    print("//////////////////////HAUSDORF//////////////////////")
    hausdorffDistance = compressionEvaluation.HausdorffDistance(originalMesh.vertices, decompression.vertices)
    print("HAUSDORFF distance: " + str(hausdorffDistance))

    print("//////////////////////ENCRYPTION//////////////////////")
    # print("keyXor = " , keyXOR)
    # print("keyShuffling = " , keyShuffling)