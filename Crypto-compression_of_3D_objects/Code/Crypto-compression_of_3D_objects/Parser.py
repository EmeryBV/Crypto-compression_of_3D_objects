import math
import trimesh
import numpy as np
import networkx as nx

from Edge import Edge
from Face import Face
from Vertex import Vertex


def getNeighbors(vertex, faces):
    neighbors = set()
    for l in faces:
        if vertex in l:
            neighbors = set.union(neighbors, set(v for v in l if v != vertex))

    return neighbors


def project(planeVertex, planeNormal, vertex):
    vec = np.subtract(vertex, planeVertex)
    return np.subtract(vertex, np.dot(vec, planeNormal) * planeNormal)


def sortNeighbors(mesh):
    g = nx.from_edgelist(mesh.edges_unique)
    one_ring = [list(g[i].keys()) for i in range(len(mesh.vertices))]
    one_ordered = [nx.cycle_basis(g.subgraph(i))[0] for i in one_ring]

    for i in range(0, len(mesh.vertices)):

        argSort = trimesh.points.radial_sort( [ np.asarray( mesh.vertices[n] ) for n in one_ordered[i]], mesh.vertices[i], mesh.vertex_normals[i])
        one_ordered[i] = [ one_ordered[i][j] for j in argSort ]
        one_ordered[i].reverse()

        # if np.dot(mesh.vertex_normals[i], [0., 0., 1.]) > 0.:
        #     print( mesh.vertex_normals[i], np.dot(mesh.vertex_normals[i], [0., 0., 1.])  )
        #     one_ordered[i].reverse()
        #     print( i, one_ordered[i] )

    return one_ordered


def readMesh(file):
    trimesh.util.attach_to_log()
    mesh = trimesh.load_mesh(file, "obj", process=False, maintain_order=True)
    meshVertices = np.asarray(mesh.vertices)
    meshTriangles = np.asarray(mesh.faces)
    meshNormals = np.asarray(mesh.vertex_normals)

    neighbors = sortNeighbors(mesh)
    vertices = []
    allEdges = {}
    for i in range(0, len(meshVertices)):
        edges = []
        for n in neighbors[i]:
            if (i, n) in allEdges.keys():
                edges.append(allEdges[(i, n)])
            elif (n, i) in allEdges.keys():
                edges.append(allEdges[(n, i)])
            else:
                allEdges[(i, n)] = Edge([i, n])
                edges.append( allEdges[(i, n)] )

        vertices.append(Vertex(i, meshVertices[i], neighbors[i], edges, normal =meshNormals[i]))
        # print( i, len(neighbors[i]), [edge.vertices for edge in edges] )

    faces = []
    for i in range(0, len(meshTriangles)):
        edges = []
        face = meshTriangles[i]

        if (face[0], face[1]) in allEdges.keys():
            edges.append( allEdges[(face[0], face[1])] )
        else:
            edges.append( allEdges[(face[1], face[0])] )

        if (face[0], face[2]) in allEdges.keys():
            edges.append( allEdges[(face[0], face[2])] )
        else:
            edges.append( allEdges[(face[2], face[0])] )

        if (face[1], face[2]) in allEdges.keys():
            edges.append( allEdges[(face[1], face[2])] )
        else:
            edges.append( allEdges[(face[2], face[1])] )

        faces.append(Face([vertices[face[0]], vertices[face[1]], vertices[face[2]]], edges))

    return vertices, faces


def writeMesh(listVertice, faces, filename):
    trimesh.util.attach_to_log()
    listPosition = []
    listIndex = []
    listNormal = []

    for vertex in listVertice:
        listPosition.append(vertex.position)
        listNormal.append(vertex.normal)

    for triangle in faces:
        listListIndex = []
        for vertex in triangle.vertices:
            listListIndex.append(vertex.index)
        listIndex.append(listListIndex)

    mesh = trimesh.Trimesh(listPosition, listIndex, process=False,vertex_normals=listNormal, maintain_order=True)

    trimesh.repair.fix_winding(mesh)

    meshText = trimesh.exchange.obj.export_obj(mesh,include_normals = True,digits=0)
    file = open(filename, "w")
    file.write(meshText)
