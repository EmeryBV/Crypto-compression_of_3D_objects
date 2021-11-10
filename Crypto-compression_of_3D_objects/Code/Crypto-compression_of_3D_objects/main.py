import Compression
import sys

def create_compress_file(filename):
    file = open(filename ,"x")
    return file



if __name__ == '__main__':
    filename = "compressMesh"
    file = create_compress_file(filename)
    file.write("test")
    Compression.Procedure_EncoreConnectivity(filename)


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
