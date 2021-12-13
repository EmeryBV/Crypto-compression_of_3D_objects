def compterOccurences(texte):
    lettres = [[0, chr(i)] for i in range(256)]
    for i in texte:
        lettres[ord(i)][0] += 1
    return lettres


def creerArbre(lettres):
    noeuds = [(k, v) for (k, v) in lettres if k > 0]
    l = len(noeuds)
    while l >= 2:
        petitMin = (0, noeuds[0])
        grandMin = (1, noeuds[1])
        for i in range(2, l):
            if noeuds[i][0] <= petitMin[1][0]:
                grandMin = petitMin
                petitMin = (i, noeuds[i])
            elif noeuds[i][0] <= grandMin[1][0]:
                grandMin = (i, noeuds[i])
        nouveauNoeud = (
            petitMin[1][0] + grandMin[1][0],
            noeuds[petitMin[0]],
            noeuds[grandMin[0]]
        )
        noeuds[petitMin[0]] = nouveauNoeud
        noeuds.pop(grandMin[0])
        l -= 1
    return noeuds[0]

def creerDico(arbre):

    fileExploration = [("", arbre)]
    dico = {}
    l = 1
    while l >= 1:
        code, truc = fileExploration.pop(0)
        l -= 1
        if len(truc) == 2:
            dico[truc[1]] = code
        elif len(truc) == 3:
            fileExploration.append((code + "0", truc[1]))
            fileExploration.append((code + "1", truc[2]))
            l += 2
    return dico


def compresser(texte):
    lettres = compterOccurences(texte)
    arbre = creerArbre(lettres)
    dico = creerDico(arbre)
    texteCompresse = ""
    for i in texte:
        texteCompresse += dico[i]
    return texteCompresse, dico


def decompresser(texteCompresse, dicoRetourne):
    dico = {v: k for (k, v) in dicoRetourne.items()}
    limite = max(len(k) for k in dico.keys())
    fileExploration = [("", texteCompresse)]
    l = 1
    while l >= 1:
        fait, restant = fileExploration.pop(0)
        l -= 1
        if restant == "":
            return fait
        i = 0
        bits = ""
        for bit in restant:
            bits += bit
            i += 1
            if i > limite:
                break
            elif bits in dico:
                fileExploration.append((fait + dico[bits], restant[i:]))
                l += 1
    return None
