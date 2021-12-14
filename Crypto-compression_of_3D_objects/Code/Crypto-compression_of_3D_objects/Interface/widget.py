import re
import ast
import sys
import copy

import trimesh

from random import randint

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QFileDialog

from Parser import readMesh, readMeshBis
from Interface.mainWindow import Ui_MainWindow
from Compression import Compression, Decompression

ui = Ui_MainWindow()

meshFile = ""
compressedMesh=""
seed = ""
quantification = ""

keyXOR = ""
keyShuffling = ""
filepathDestination =""
filepathDestination2 =""
filePathCompressFile=""
modeCompression = ""
modeDecompression = ""

def buttonSetUpCompression(ui):
    ui.browse.clicked.connect(browseFile)
    ui.browseDestinationFile.clicked.connect(browseDestinationFile)
    ui.generateSeed.clicked.connect(generateSeed)
    ui.execute.clicked.connect(compression)


def browseFile():
    fname = QFileDialog.getOpenFileName( caption='Open file',directory="../Mesh/OBJ/simpleSphere.obj")
    ui.filePath.setText(fname[0])

def browseDestinationFile():
    fname = QFileDialog.getSaveFileName( caption='Open file', directory="../results/interface/" )
    ui.filepathDestination.setText(fname[0])

def generateSeed():
    number = randint(10000000000,100000000000000)
    ui.seed.setText(str(number))

def getValueCompression():
    global meshFile,seed,quantification,modeCompression

    meshFile = ui.filePath.text()
    modeCompression = ui.encodeMode.currentText()
    seed = ui.seed.text()
    print(meshFile)

    if not meshFile.endswith(".obj") :
        QtWidgets.QMessageBox.critical( MainWindows, "Error", "Seul les OBJ sont supportés")
        return None
    if not meshFile or not seed or not ui.filepathDestination.text():
        QtWidgets.QMessageBox.critical( MainWindows, "Error", "Remplissez tous les champs")
        return None

    seed = int(ui.seed.text())
    quantification = int(re.findall(r'\d+', ui.quantification.currentText())[0])
    return True

def compression():
    if not getValueCompression():
        return

    vertices, faces = readMesh(meshFile)

    compressedMesh = ui.filepathDestination.text()
    originalMesh = Compression.Compression(vertices, faces, compressedMesh)
    compression = copy.deepcopy(originalMesh)

    if modeCompression == "Encode connectivity + geometry":
        compression.encodeConnectivity()
        keyXOR, keyShuffling = compression.encodeGeometrySinceConnectivity(seed, quantification)
        Compression.compressionHuffman(compressedMesh, compressedMesh+"binary" )
        ui.shufflingKey.setText(str(keyShuffling))
        ui.XORKey.setText(str(keyXOR))
        ui.copyShuffling.setEnabled(True)
        ui.copyXOR.setEnabled(True)
        ui.shufflingKey.setEnabled(True)
        ui.XORKey.setEnabled(True)
        ui.copyShuffling.clicked.connect(copyKeyShuffling)
        ui.copyXOR.clicked.connect(copyKeyXOR)

    elif modeCompression == "Encode geometry":
        compressedMesh += ".obj"
        keyXOR, keyShuffling = compression.encodeGeometryWithoutConnectivity(seed, quantification, compressedMesh)
        compressBinary = compressedMesh.replace(".obj", "binary")
        Compression.compressionHuffman(compressedMesh, compressBinary)
        ui.shufflingKey.setText(str(keyShuffling))
        ui.XORKey.setText(str(keyXOR))
        ui.copyShuffling.setEnabled(True)
        ui.copyXOR.setEnabled(True)
        ui.shufflingKey.setEnabled(True)
        ui.XORKey.setEnabled(True)
        ui.copyShuffling.clicked.connect(copyKeyShuffling)
        ui.copyXOR.clicked.connect(copyKeyXOR)

def buttonSetUpDecompression(ui):
    ui.browse_2.clicked.connect(browseFilesDecompression)
    ui.execute2.clicked.connect(decompression)
    ui.browseDestinationFile_2.clicked.connect(browseDestinationFileDecompress)

def browseDestinationFileDecompress():
    fname = QFileDialog.getSaveFileName( caption='Open file', directory="../results/interface/" ,filter=".obj",initialFilter=".obj" )
    ui.filepathDestination_2.setText(fname[0]+".obj")

def browseFilesDecompression():
    fname = QFileDialog.getOpenFileName( caption='Open file',directory="../results/interface/")
    ui.filePathCompressFile.setText(fname[0])

def getValueDecompression():
    global keyXOR,keyShuffling,filepathDestination2, filePathCompressFile, modeDecompression
    filePathCompressFile = ui.filePathCompressFile.text()
    filepathDestination2 = ui.filepathDestination_2.text()

    keyXOR = ui.XORKeyDecrypt.text()
    keyShuffling= ui.shufflingKeyDecrypt.text()
    modeDecompression = ui.decodeMode.currentText()

    if not filepathDestination2 or not filePathCompressFile or not keyShuffling or not keyXOR:
        QtWidgets.QMessageBox.critical(MainWindows, "Error", "Remplissez tous les champs")
        return None

    keyXOR = ast.literal_eval(keyXOR)

    keyShuffling = ast.literal_eval(keyShuffling)
    return True

def decompression():
    if not getValueDecompression():
        return
    decompressedMeshHuffman = "decompressedMeshHuffman"
    Decompression.decompressionHuffman(filePathCompressFile, decompressedMeshHuffman)
    if modeDecompression == "Decode connectivity + geometry":
        decompression = Decompression.Decompression(decompressedMeshHuffman, filepathDestination2, keyXOR, keyShuffling)
        decompression.decodeConnectivity()
    elif modeDecompression == "Decode geometry":
        vertices, faces = readMeshBis(decompressedMeshHuffman)
        decompression = Decompression.Decompression(decompressedMeshHuffman, filepathDestination2, keyXOR, keyShuffling, vertices,faces )
        decompression.decodeGeometryNotSinceConnectivity()

    mesh = trimesh.load( filepathDestination2 )
    mesh.show(flags={'wireframe': True})

def copyKeyShuffling():
    ui.shufflingKey.selectAll()
    ui.shufflingKey.copy()


def copyKeyXOR():
    ui.XORKey.selectAll()
    ui.XORKey.copy()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    global MainWindows
    MainWindows = QtWidgets.QMainWindow()

    ui.setupUi(MainWindows)
    buttonSetUpCompression(ui)
    buttonSetUpDecompression(ui)
    MainWindows.show()

    sys.exit(app.exec())
