# This Python file uses the following encoding: utf-8
import copy
import sys

from PyQt5 import QtWidgets
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QFileDialog

from Interface.mainWindow import Ui_MainWindow
from Parser import readMesh
from Compression import Compression, Decompression
from random import randint
import re
import ast
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
    seed = int(ui.seed.text())
    quantification = int(re.findall(r'\d+', ui.quantification.currentText())[0])
    modeCompression = ui.encodeMode.currentText()


def compression():
    getValueCompression()

    vertices, faces = readMesh(meshFile)
    print(meshFile)
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
        print("Encode geometry")
        compressedMesh += ".obj"
        keyXOR, keyShuffling = compression.encodeGeometryWithoutConnectivity(seed, quantification, compressedMesh)
        compressBinary = compressedMesh.replace(".obj", "binary")
        print(compressBinary)
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
    modeCompression = ui.encodeMode.currentText()

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
    print(len(keyXOR))
    keyXOR = ast.literal_eval(keyXOR)
    print(keyXOR)
    print(keyXOR[0][0])
    keyShuffling= ui.shufflingKeyDecrypt.text()
    keyShuffling = ast.literal_eval(keyShuffling)

def decompression():
    getValueDecompression()
    decompressedMeshHuffman = "decompressedMeshHuffman"
    Decompression.decompressionHuffman(filePathCompressFile, decompressedMeshHuffman)

    if modeCompression == "Encode connectivity + geometry":
        decompression = Decompression.Decompression(decompressedMeshHuffman, filepathDestination2, keyXOR, keyShuffling)
        decompression.decodeConnectivity()
    elif modeCompression == "Encode geometry":
        print("here")
        vertices, faces = readMesh(decompressedMeshHuffman)
        print(vertices)
        print(faces)
        decompression = Decompression.Decompression(decompressedMeshHuffman, filepathDestination2, keyXOR, keyShuffling, vertices,faces )
        decompression.decodeGeometryNotSinceConnectivity()

def copyKeyShuffling():
    ui.shufflingKey.selectAll()
    ui.shufflingKey.copy()


def copyKeyXOR():
    ui.XORKey.selectAll()
    ui.XORKey.copy()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindows = QtWidgets.QMainWindow()
    ui.setupUi(MainWindows)
    buttonSetUpCompression(ui)
    buttonSetUpDecompression(ui)
    MainWindows.show()

    sys.exit(app.exec())