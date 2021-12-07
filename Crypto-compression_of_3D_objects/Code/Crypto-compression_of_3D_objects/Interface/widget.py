# This Python file uses the following encoding: utf-8
import copy
import sys

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QFileDialog

from Interface.mainWindow import Ui_MainWindow
from Parser import readMesh
from Compression import Compression, Decompression
from random import randint
import re
ui = Ui_MainWindow()

meshFile = ""
compressedMesh=""
seed = ""
quantification = ""

keyXOR = ""
keyShuffling = ""
filepathDestination2 =""
filePathCompressFile=""
def buttonSetUpCompression(ui):
    ui.browse.clicked.connect(browseFilesCompression)
    ui.execute.clicked.connect(compression)

    ui.generateSeed.clicked.connect(generateSeed)


def browseFilesCompression():
    fname = QFileDialog.getOpenFileName( caption='Open file',directory="/home/bourget-vecchio/Documents/Master_IMAGINA/M2/PROJET IMAGE/Crypto-compression_of_3D_objects/Code/Crypto-compression_of_3D_objects/Mesh/OBJ/simpleSphere.obj")
    ui.filePath.setText(fname[0])

def generateSeed():
    number = randint(10000000000,100000000000000)
    ui.seed.setText(str(number))

def getValueCompression():
    global meshFile,seed,quantification
    meshFile = ui.filePath.text()
    seed = int(ui.seed.text())
    quantification = int(re.findall(r'\d+', ui.quantification.currentText())[0])

def compression():
    getValueCompression()
    print(meshFile)
    print(seed)
    print(quantification)
    vertices, faces = readMesh(meshFile)
    compressedMesh = ui.filepathDestination.text()
    originalMesh = Compression.Compression(vertices, faces, compressedMesh)
    compression = copy.deepcopy(originalMesh)
    compression.encodeConnectivity()
    keyXOR, keyShuffling = compression.encodeGeometry(seed, quantification)
    Compression.compressionMarkov(compressedMesh, compressedMesh + "Markov")
    ui.shufflingKey.setText(str(keyShuffling))
    ui.XORKey.setText(str(keyXOR))
    ui.copyShuffling.setEnabled(True)
    ui.copyXOR.setEnabled(True)
    ui.shufflingKey.setEnabled(True)
    ui.XORKey.setEnabled(True)
    ui.copyShuffling.clicked.connect(copyKeyShuffling)
    ui.copyXOR.clicked.connect(copyKeyXOR)

def buttonSetUpDecompression(ui):
    ui.browse_2.clicked.connect(browseFilesDeompression)
    ui.execute2.clicked.connect(decompression)


def browseFilesDeompression():
    fname = QFileDialog.getOpenFileName( caption='Open file',directory="/home/bourget-vecchio/Documents/Master_IMAGINA/M2/PROJET IMAGE/Crypto-compression_of_3D_objects/Code/Crypto-compression_of_3D_objects/results")
    ui.filePathCompressFile.setText(fname[0])


def getValueDecompression():
    global keyXOR,keyShuffling,filepathDestination2, filePathCompressFile
    filePathCompressFile = ui.filePathCompressFile.text()
    filepathDestination2 = ui.filepathDestination2.text()
    keyXOR = ui.XORKeyDecrypt.text()
    keyShuffling= ui.shufflingKeyDecrypt.text()


def decompression():
    getValueCompression()
    decompressedMeshMarkov = "decompressedMeshMarkov"
    Decompression.decompressionMarkov(filepathDestination2, decompressedMeshMarkov)
    decompression = Decompression.Decompression(decompressedMeshMarkov, filepathDestination2, keyXOR, keyShuffling)
    decompression.decodeConnectivity()


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