# This Python file uses the following encoding: utf-8
import copy
import sys

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow,QFileDialog

from Interface.mainWindow import Ui_MainWindow
from Parser import readMesh
from Compression import Compression
from Compression import Decompression
from Evaluation import compressionEvaluation
from main import create_compress_file

ui = Ui_MainWindow()
meshFile = ""
compressedMesh=""

def buttonSetUp(ui):
    ui.browse.clicked.connect(browseFiles)
    ui.execute.clicked.connect(compression)


def browseFiles():
    fname = QFileDialog.getOpenFileName( caption='Open file')
    ui.filePath.setText(fname[0])


def compression():
    meshFile = ui.filePath.text()
    print(meshFile)
    vertices, faces = readMesh(meshFile)
    compressedMesh = ui.filepathDestination.text()
    originalMesh = Compression.Compression(vertices, faces, compressedMesh)
    compression = copy.deepcopy(originalMesh)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindows = QtWidgets.QMainWindow()
    ui.setupUi(MainWindows)
    buttonSetUp(ui)
    MainWindows.show()



    sys.exit(app.exec())