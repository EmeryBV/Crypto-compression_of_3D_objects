from Parser import readMesh
from Compression import Compression, Decompression
from Evaluation import compressionEvaluation
import copy

def create_compress_file(filename):
    file = open(filename, "w")
    return file


if __name__ == '__main__':
    compressedMesh = "results/compressedMesh.txt"
    compressedMeshMarkov = "results/compressedMeshMarkov.txt"
    decompressedMeshMarkov = "results/DecompressedMeshMarkov"
    decompressedMesh = "results/DecompressedMesh2.obj"
    file = create_compress_file(compressedMesh)
    # file.write("test.obj")
    meshFile = "./Mesh/OBJ/suzanne.obj"
    seed = 2563
    quantification = 1024
    vertices, faces = readMesh(meshFile)
    originalMesh = Compression.Compression(vertices, faces, compressedMesh)
    compression = copy.deepcopy(originalMesh)

    compression.encodeConnectivity()
    keyXOR, keyShuffling = compression.encodeGeometry(seed,quantification)

    Compression.compressionMarkov(compressedMesh, compressedMeshMarkov)

    print("//////////////////////DECOMPRESSION//////////////////////")
    Decompression.decompressionMarkov(compressedMeshMarkov, decompressedMeshMarkov)
    decompression = Decompression.Decompression(decompressedMeshMarkov, decompressedMesh, keyXOR, keyShuffling)
    decompression.decodeConnectivity()

    print("//////////////////////HAUSDORF//////////////////////")
    hausdorffDistance = compressionEvaluation.HausdorffDistance(originalMesh.vertices, decompression.vertices)
    print("HAUSDORFF distance: " + str(hausdorffDistance))
    print("//////////////////////ENCRYPTION//////////////////////")
    print("keyXor = " , keyXOR)
    print("keyShuffling = " , keyShuffling)