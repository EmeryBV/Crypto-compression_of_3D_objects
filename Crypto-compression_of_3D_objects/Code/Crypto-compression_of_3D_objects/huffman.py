def compterOccurences(texte):
    lettres = [[0, chr(i)] for i in range(256)]
    for i in texte:
        lettres[ord(i)][0] += 1
    return lettres

def creerArbre(lettres):
    # On commence par enlever les lettres qui ne sont pas présentes
    noeuds = [(k, v) for (k, v) in lettres if k > 0]
    # Puis on récupère les deux noeuds (ou feuilles) de poids le plus faible,
    # et on en fait un noeud, de poids la somme des deux petits poids
    # On boucle tant qu'il y a reste au moins deux noeuds
    l = len(noeuds)
    while l >= 2:
        # Indice et noeud des minima des poids
        # (on initialise avec les deux premières valeurs)
        petitMin = (0, noeuds[0])
        grandMin = (1, noeuds[1])
        for i in range(2, l):
            if noeuds[i][0] <= petitMin[1][0]:  # poids < petitMin < grandMin
                grandMin = petitMin
                petitMin = (i, noeuds[i])
            elif noeuds[i][0] <= grandMin[1][0]:  # petitMin < poids < grandMin
                grandMin = (i, noeuds[i])
        nouveauNoeud = (
            petitMin[1][0] + grandMin[1][0],
            noeuds[petitMin[0]],
            noeuds[grandMin[0]]
        )
        # On enlève les deux noeuds (ou feuilles) précedentes
        # et on ajoute le nouveau noeud
        noeuds[petitMin[0]] = nouveauNoeud
        noeuds.pop(grandMin[0])
        # On a au final un noeud de moins (-2 +1)
        l -= 1
    # À cet instant il ne reste plus qu'un noeud, qui est la racine de
    # l'arbre de Huffman
    return noeuds[0]

def creerDico(arbre):
    fileExploration = [("", arbre)]
    dico = {}
    l = 1
    # On boucle tant que la file n'est pas vide
    while l >= 1:
        code, truc = fileExploration.pop(0)  # On défile le premier élément
        l -= 1
        if len(truc) == 2:  # C'est une feuille
            dico[truc[1]] = code  # On ajoute la lettre et son code au dico
        elif len(truc) == 3:  # C'est un noeud
            # On continue l'exploration en respectant la règle pour obtenir le code :
            # Gauche -> 0, droite -> 1
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
    # On n'oublie pas de renvoyer aussi le dictionnaire,
    # sinon il sera impossible de décompresser le texte
    return texteCompresse, dico

def decompresser(texteCompresse, dicoRetourne):
    # On retourne le dico
    dico = {v: k for (k, v) in dicoRetourne.items()}
    # Nombre maximum de bits d'un caractère compressé
    limite = max(len(k) for k in dico.keys())
    fileExploration = [("", texteCompresse)]
    l = 1
    while l >= 1:
        fait, restant = fileExploration.pop(0)  # On défile le premier élément
        l -= 1
        # On regarde si la décompression est terminée
        if restant == "":
            return fait
        # Sinon, on tente de remplacer les i premiers bits de restant par un caractère
        i = 0
        bits = ""
        for bit in restant:
            bits += bit
            i += 1
            if i > limite:
                # C'est pas la peine de continuer, bits est trop long
                # pour correspondre à un caractère
                break
            elif bits in dico:
                # On a la possibilité de remplacer quelques 0 et 1 par un caractère
                # alors on le fait, sans pour autant considérer que l'on a choisi
                # le bon remplacement
                fileExploration.append((fait + dico[bits], restant[i:]))
                l += 1
                # Puis on continue à explorer les possibilités
    # Aucune décompression n'a fonctionné, on ne renvoie rien
    return None

