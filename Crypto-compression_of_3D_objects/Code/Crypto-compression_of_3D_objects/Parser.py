import math
import trimesh
import numpy as np
import networkx as nx

from Face import Face
from Vertex import Vertex


def getNeighbors( vertex, faces ):

    neighbors = set()
    for l in faces:
        if vertex in l:
            neighbors = set.union( neighbors, set( v for v in l if v != vertex ) )

    return neighbors


def project( planeVertex, planeNormal, vertex ):
    vec = np.subtract( vertex, planeVertex )
    return np.subtract( vertex, np.dot( vec, planeNormal ) * planeNormal )


def sortNeighbors( mesh ):

    g = nx.from_edgelist( mesh.edges_unique )
    one_ring    = [ list( g[i].keys() ) for i in range( len( mesh.vertices ) ) ]
    one_ordered = [ nx.cycle_basis( g.subgraph( i ) )[0] for i in one_ring ]

    for i in range( 0, len( mesh.vertices ) ):
        if np.dot( mesh.vertex_normals[ i ], [ 0., 0., 1. ] ) > 0.:
            # print(i)
            one_ordered[i].reverse()

    return one_ordered


def readMesh( file ):

    trimesh.util.attach_to_log()
    mesh = trimesh.load_mesh( file, "obj", process = False, maintain_order = True )

    meshVertices  = np.asarray( mesh.vertices       )
    meshTriangles = np.asarray( mesh.faces          )
    meshNormals   = np.asarray( mesh.vertex_normals )

    neighbors = sortNeighbors( mesh )

    vertices = []
    for i in range( 0, len( meshVertices ) ):
        vertices.append( Vertex( i, meshVertices[i], neighbors[i] ) )
        # print( i, meshVertices[i], meshNormals[i], neighbors[i] )

    faces = []
    for i in range(0, len(meshTriangles)):
        face = meshTriangles[i]
        faces.append( Face( [vertices[face[0]], vertices[face[1]], vertices[face[2]]] ) )

    return vertices, faces


def writeMesh( listVertice, faces ):

    trimesh.util.attach_to_log()
    listPosition = []
    listIndex = []

    for vertex in listVertice:
        listPosition.append( vertex.position )

    for triangle in faces:
        listListIndex = []
        for vertex in triangle.vertices:
            listListIndex.append( vertex.index )
        listIndex.append( listListIndex )

    mesh = trimesh.Trimesh( listPosition, listIndex, process = False, maintain_order = True )

    meshText = trimesh.exchange.obj.export_obj( mesh )
    file = open( "test.obj", "w" )
    file.write( meshText )
