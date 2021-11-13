import math
import numpy as np

import trimesh

from Vertex import Vertex
from Face import Face


def getNeighbors(vertex, faces):
    neighbors = set()
    for l in faces:
        if vertex in l:
            set.union(neighbors, set(v for v in l if v != vertex
    return neighbors


def sortNeighbors(vertex, vertices, neighbors):
    upVector = np.array([0., 1., 0.])
    vertexPos = vertices[vertex]

    angles = {}

    for n in neighbors:
        nPos = vertices[n]
        normalizedVec = np.linalg.norm(nPos.substract(vertexPos))
        angles[n] = math.acos(np.dot(upVector, normalizedVec)) * 180. / np.pi

    sortedNeighbors = {k: v for k, v in sorted(angles.items(), key=lambda item: item[1], reverse=True)}
    return sortedNeighbors.keys()


def readMesh(file):
    trimesh.util.attach_to_log()
    mesh = trimesh.load( file )

    meshVertices = np.asarray(mesh.vertices)
    meshTriangles = np.asarray(mesh.faces)

    neighbors = {}
    for i in range(0, len(meshVertices)):
        neighbors[i] = sortNeighbors(i, meshVertices, getNeighbors(i, meshTriangles))

    vertices = []
    for i in range(0, len(meshVertices)):
        vertices.append(Vertex(i, meshVertices[i], neighbors[i]))

    faces = []
    for i in range(0, len(meshTriangles)):
        face = meshTriangles[i]
        faces.append(Face([vertices[face[0]], vertices[face[1]], vertices[face[2]]]))

    return vertices, faces
