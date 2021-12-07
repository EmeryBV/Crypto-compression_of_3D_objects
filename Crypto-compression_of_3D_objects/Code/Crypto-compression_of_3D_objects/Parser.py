import open3d.cpu.pybind.geometry

import objParser
import pprint
import trimesh
import open3d as o3d
import numpy as np
from collections import OrderedDict

from MeshData.Edge import Edge
from MeshData.Face import Face
from MeshData.Vertex import Vertex
import sys
import numpy

numpy.set_printoptions(threshold=sys.maxsize)


def radial_sort(points,
                origin,
                normal):
    # create two axis perpendicular to each other and the normal,
    # and project the points onto them
    axis0 = [normal[0], normal[2], -normal[1]]
    axis1 = np.cross(normal, axis0)
    ptVec = points - origin
    pr0 = np.dot(ptVec, axis0)
    pr1 = np.dot(ptVec, axis1)

    # calculate the angles of the points on the axis
    angles = np.arctan2(pr0, pr1)

    # return the points sorted by angle
    return np.argsort(angles)


def project(planeVertex, planeNormal, vertex):
    vec = np.subtract(vertex, planeVertex)
    return np.subtract(vertex, np.dot(vec, planeNormal) * planeNormal)


def sortNeighbors2(vertices, normals, neighbors):
    sortedNeighbors = {}
    for i in range(0, len(vertices)):
        projectedPoints = []
        for n in neighbors[i]:
            projectedPoints.append(project(vertices[i], normals[i], vertices[n]))
        vec = projectedPoints[0] - vertices[i]
        a = {}
        a[list(neighbors[i])[0]] = 0.
        for j in range(1, len(neighbors[i])):
            n = list(neighbors[i])[j]
            vec2 = projectedPoints[j] - vertices[i]
            cross = np.cross(vec, vec2)
            crossL = np.linalg.norm(cross)
            angle = np.math.atan2(np.dot(cross, normals[i]), np.dot(vec, vec2))
            a[n] = angle * 180. / np.pi
            if a[n] < 0.:
                a[n] += 360.

        ordered_dic = OrderedDict(sorted(a.items(), key=lambda t: t[1]))
        sortedNeighbors[i] = ordered_dic

    final = []
    for sortedN in sortedNeighbors.items():
        final.append(list(sortedN[1].keys()))

    return final


def readMesh(file):
    mesh = o3d.io.read_triangle_mesh(file)
    mesh.remove_duplicated_vertices()
    mesh.compute_vertex_normals()

    meshVertices = (np.asarray(mesh.vertices))
    meshTriangles = (np.asarray(mesh.triangles))
    meshNormals = (np.asarray(mesh.vertex_normals))
    meshTexture = (np.asarray(mesh.triangle_uvs))
    neighbors = dict()
    for triangle in meshTriangles:
        v0 = triangle[0]
        v1 = triangle[1]
        v2 = triangle[2]
        if v0 in neighbors.keys():
            neighbors[v0] = set.union(neighbors[v0], {v1, v2})
        else:
            neighbors[v0] = {v1, v2}
        if v1 in neighbors.keys():
            neighbors[v1] = set.union(neighbors[v1], {v0, v2})
        else:
            neighbors[v1] = {v0, v2}
        if v2 in neighbors.keys():
            neighbors[v2] = set.union(neighbors[v2], {v0, v1})
        else:
            neighbors[v2] = {v0, v1}

    neighbors = sortNeighbors2(meshVertices, meshNormals, neighbors)
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
                edges.append(allEdges[(i, n)])
        vertices.append(Vertex(i, meshVertices[i], neighbors[i], edges, normal=meshNormals[i], texture=meshTexture[i]))

    faces = []
    for i in range(0, len(meshTriangles)):
        edges = []
        face = meshTriangles[i]
        if (face[0], face[1]) in allEdges.keys():
            edges.append(allEdges[(face[0], face[1])])
        else:
            edges.append(allEdges[(face[1], face[0])])

        if (face[0], face[2]) in allEdges.keys():
            edges.append(allEdges[(face[0], face[2])])
        else:
            edges.append(allEdges[(face[2], face[0])])

        if (face[1], face[2]) in allEdges.keys():
            edges.append(allEdges[(face[1], face[2])])
        else:
            edges.append(allEdges[(face[2], face[1])])

        faces.append(Face([vertices[face[0]], vertices[face[1]], vertices[face[2]]], edges))

    return vertices, faces


def writeMesh(listVertice, faces, filename, precision):
    trimesh.util.attach_to_log()
    listPosition = []
    listIndex = []
    listNormal = []
    listTexture = []

    for vertex in listVertice:
        listPosition.append(vertex.position)
        listNormal.append(vertex.normal)
    vertice = open3d.utility.Vector3dVector(listPosition)
    normals = open3d.utility.Vector3dVector(listNormal)
    dico = []
    for triangle in faces:
        listListIndex = []
        for vertex in triangle.vertices:
            listListIndex.append(vertex.index)
            if vertex.index not in dico:
                listTexture.append(vertex.texture)
                dico.append(vertex.index)



        listIndex.append(listListIndex)
    indexTriangle = open3d.utility.Vector3iVector(listIndex)

    mesh = trimesh.Trimesh(listPosition, listIndex, process=False, vertex_normals=listNormal, maintain_order=True)

    trimesh.repair.fix_inversion(mesh,True)
    trimesh.repair.fix_winding(mesh)

    mesh.visual = trimesh.visual.texture.TextureVisuals(listTexture)
    mesh.vertex_normals = listNormal
    trimesh.repair.fix_winding(mesh)
    trimesh.repair.fix_inversion(mesh, True)
    meshText = trimesh.exchange.obj.export_obj(mesh, include_normals=True, include_texture=True, digits=precision)

    file = open(filename, "w")
    file.write(meshText)
