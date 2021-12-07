import re
import numpy as np

vertexRegex = r"v (\-*\d+\.*\d*)\s(\-*\d+\.*\d*)\s(\-*\d+\.*\d*)"
normalRegex = r"vn (\-*\d+\.*\d*)\s(\-*\d+\.*\d*)\s(\-*\d+\.*\d*)"
texCoordRegex = r"vt (\-*\d+\.*\d*)\s(\-*\d+\.*\d*)"
faceWithoutTexture = r"f (\d+)//(\d+) (\d+)//(\d+) (\d+)//(\d+)"
faceWithTexture = r"f (\d+)/(\d+)/(\d+) (\d+)/(\d+)/(\d+) (\d+)/(\d+)/(\d+)"

def parseOBJ( filename ):
    vertices = []
    faces = []
    normals = []
    textures = []
    sortedNormals = {}
    sortedTextures = {}

    with open( filename ) as file:
        content = file.readlines()
        for line in content:
            if line.startswith('v '):
                match = re.match(vertexRegex, line )
                vertices.append([ float( match.groups()[0]), float( match.groups()[1]), float( match.groups()[2]) ])

            elif line.startswith('vn '):
                match = re.search( normalRegex, line)
                normals.append([ float( match.groups()[0]), float( match.groups()[1]), float( match.groups()[2]) ])

            elif line.startswith('vt '):
                match = re.search( texCoordRegex, line )
                textures.append([ float( match.groups()[0]), float( match.groups()[1])])

            elif line.startswith('f '):
                if not textures:
                    match = re.search( faceWithoutTexture, line )
                    computeFace(match.groups()[0:2], normals, textures, sortedNormals, sortedTextures)
                    computeFace(match.groups()[2:4], normals, textures, sortedNormals, sortedTextures)
                    computeFace(match.groups()[4:6], normals, textures, sortedNormals, sortedTextures)
                    faces.append([int(match.groups()[0])-1, int(match.groups()[2])-1, int(match.groups()[4])-1])
                else:
                    match = re.search( faceWithTexture, line )
                    computeFace(match.groups()[0:3], normals, textures, sortedNormals, sortedTextures, hasTexture = True)
                    computeFace(match.groups()[3:6], normals, textures, sortedNormals, sortedTextures, hasTexture = True)
                    computeFace(match.groups()[6:9], normals, textures, sortedNormals, sortedTextures, hasTexture = True)
                    faces.append([int(match.groups()[0])-1, int(match.groups()[3])-1, int(match.groups()[6])-1])

        for i in range(len(vertices)):
            print(i, vertices[i], sortedNormals[i])

        return np.asarray(vertices), np.asarray(list(sortedNormals.values())), np.asarray(faces), np.asarray(sortedTextures)

def computeFace( vertex, normals, textures, sortedNormals, sortedTextures, hasTexture = False ):
    if hasTexture:
        sortedTextures[int(vertex[0])-1] = textures[int(vertex[1])-1]
        sortedNormals[int(vertex[0])-1] = normals[int(vertex[2])-1]
    else:
        sortedNormals[int(vertex[0])-1] = normals[int(vertex[1])-1]

