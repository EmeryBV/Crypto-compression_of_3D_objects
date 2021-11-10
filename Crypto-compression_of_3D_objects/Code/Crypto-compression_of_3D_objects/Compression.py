from ActiveList import ActiveList


def EncoreConnectivity(filename):
    file = open(filename, "x")
    stack = []
    AL = ActiveList()
    AL1 = ActiveList()
    while 1:
    # TODO: Selection d'un triangle aléatoire non visité
        file.write("add "+str(1))
        file.write("add "+str(2))
        file.write("add "+str(3))
        AL.focusVertex = 1
        stack.append(AL)


# TODO: Selection d'un triangle aléatoire
