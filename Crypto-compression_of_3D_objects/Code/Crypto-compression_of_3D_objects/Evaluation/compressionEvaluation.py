from MeshData import Vertex
from scipy.spatial.distance import directed_hausdorff


def HausdorffDistance(originalMesh, modifiedMesh):

    arrayOriginalMesh = []
    arrayModifiedMesh = []
    for idx in range(len(originalMesh)):
        arrayOriginalMesh.append(originalMesh[idx].position)
        arrayModifiedMesh.append(modifiedMesh[idx].position)
    return directed_hausdorff(arrayOriginalMesh, arrayModifiedMesh)
