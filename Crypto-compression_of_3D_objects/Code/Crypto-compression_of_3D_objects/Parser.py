import math
import numpy as np
import open3d as o3d


def getNeighbors( vertex, faces ):
    neighbors = set()
    for l in faces:
        if vertex in l:
            neighbors.union( { v for v in l if v != vertex } )
    return neighbors


def sortNeighbors( vertex, vertices, neighbors ):
    upVector = np.array( [ 0., 1., 0. ] )
    vertexPos = vertices[ vertex ]

    angles = {}

    for n in neighbors:
        nPos = vertices[ n ]
        normalizedVec = np.linalg.norm( nPos.substract( vertexPos ) )
        angles[ n ] = math.acos( np.dot( upVector, normalizedVec ) ) * 180. /  np.pi

    sortedNeighbors = { k : v for k, v in  sorted( angles.items(), key = lambda item : item[1],  reverse = True )}
    return sortedNeighbors.keys()


def readMesh(file):
    mesh = o3d.io.read_triangle_mesh(file)

    vertices  = np.asarray(mesh.vertices)
    triangles = np.asarray(mesh.triangles)

    neighbors = {}
    for i in range ( 0 , len(vertices) + 1 ):
        neighbors[ i ] = sortNeighbors( i, vertices, getNeighbors( i ) )

    return vertices, triangles, neighbors
