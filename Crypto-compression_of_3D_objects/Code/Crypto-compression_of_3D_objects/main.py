from Parser import readMesh
from Compression import Compression
from Compression import Decompression
from Evaluation import compressionEvaluation
from Encryption import encryption
import copy

def create_compress_file(filename):
    file = open(filename, "w")
    return file


if __name__ == '__main__':
    compressedMesh = "results/compressedMesh.txt"
    compressedMeshMarkov = "results/compressedMeshMarkov.txt"
    decompressedMeshMarkov = "results/DecompressedMeshMarkov"
    decompressedMesh = "results/DecompressedMesh.obj"
    file = create_compress_file(compressedMesh)
    # file.write("test.obj")
    meshFile = "./Mesh/OBJ/simpleSphere.obj"
    seed = 2563
    vertices, faces = readMesh(meshFile)
    originalMesh = Compression.Compression(vertices, faces, compressedMesh)
    compression = copy.deepcopy(originalMesh)

    compression.encodeConnectivity()
    keyXOR, keyShuffling = compression.encodeGeometry(seed,1024)

    Compression.compressionMarkov(compressedMesh, compressedMeshMarkov)

    print("//////////////////////DECOMPRESSION//////////////////////")
    Decompression.decompressionMarkov(compressedMeshMarkov, decompressedMeshMarkov)
    decompression = Decompression.Decompression(decompressedMeshMarkov, decompressedMesh,keyXOR, keyShuffling)
    decompression.decodeConnectivity()

    print("//////////////////////HAUSDORF//////////////////////")
    hausdorffDistance = compressionEvaluation.HausdorffDistance(originalMesh.vertices, decompression.vertices)
    print("HAUSDORFF distance: " + str(hausdorffDistance))
    print("//////////////////////ENCRYPTION//////////////////////")
    print("keyXor = " , keyXOR)
    print("keyShuffling = " , keyShuffling)