from graphe import  *
from fragilite import *
from random import *
import argparse



def charger_donnees(graphe, fichier):
    file = open('données/' + fichier, mode = 'r', encoding = 'utf-8-sig')
    lines = file.readlines()
    file.close()
    for line in lines:
        array = line.split(':')
        if len(array) == 2:
            nom = array[1].split("\n")
            graphe.nom_dict[int(array[0])] = nom[0]
       
        array = line.split('/')
        if len(array) == 3:
            #print(array)
            nom = fichier.split(".txt")
            poid = array[2].split("\n")
            graphe.ajouter_arete(int(array[0]), int(array[1]), int(poid[0]), nom[0])

    pass

def numerotations(G):
    debut = dict()
    parent = dict()
    ancetre = dict()
    for sommet in G.sommets():
        debut[sommet] = 0
        parent[sommet] = None
        ancetre[sommet] = 100000000
    instant = 0
    def numerotationRecursive(s):
        nonlocal instant, debut, parent, ancetre
        instant = instant + 1
        ancetre[s] = instant
        debut[s] = ancetre[s]
        for t in G.voisins(s):
            t = t[0]
            if debut[t] != 0:
                if parent[s] != t:
                    ancetre[s] = min(ancetre[s],debut[t])
            else:
                parent[t] = s
                numerotationRecursive(t)
                ancetre[s] = min(ancetre[s], ancetre[t])
    
    for v in G.sommets():
        if debut[v] == 0:
            numerotationRecursive(v)
    
    return (debut, parent, ancetre)


def points_articulation(G : Graphe):
    tuple = numerotations(G)
    debut = tuple[0]
    parent = tuple[1]
    ancetre = tuple[2]
    articulations = []
    racines = []
    for v in G.sommets():
        if parent[v] == None:
            racines.append(v)
    
    for depart in racines:
        count = 0
        for i in parent:
            if parent[i] != None and depart == parent[i]:
                count += 1
        if count >= 2:
            articulations.append(depart)
    
    racines.append(None)
    
    for v in G.sommets():
        #print(articulations)
        if parent[v] not in racines and ancetre[v] >= debut[parent[v]] and parent[v] not in articulations:
            articulations.append(parent[v])

    retSomm = []
    for i in articulations:
        retSomm.append(i)

    return retSomm
    pass

def ponts(G : Graphe):
    tuple = numerotations(G)
    debut = tuple[0]
    parent = tuple[1]
    ancetre = tuple[2]

    res = []
   
    for arete in G.aretes():
        u = arete[0]
        v = arete[1]

        if ancetre[v] > debut[u]:
            res.append([u,v])

        elif ancetre[u] > debut[v]:
            res.append([u,v])
    
    return res

def parcour_profondeur(G : Graphe,s ,exept):
    dejaVisite = []

    def parcour(som):
        nonlocal dejaVisite
        dejaVisite.append(som)
        for voisin in G.voisins(som):
            voisin = voisin[0]
            if voisin not in dejaVisite and voisin not in exept:
                parcour(voisin)

    parcour(s)
    retVisite = []
    for i in dejaVisite:
        retVisite.append(i)
    return sorted(retVisite)
    pass

def amelioration_ponts(G : Graphe):
    retArr = []
    pon = []
    pon = sorted(map(sorted,ponts(G)))
    index = 0

    def amelioration(C,u,v):
        nonlocal pon, retArr
        exept = []
        parc = []
        for i in pon:
            exept.append(v)

        parc = parcour_profondeur(C,u,exept)
        ran = randint(0,len(parc) -1)

        c = 0
        while parc[ran] == u:
            ran = randint(0,len(parc) -1)
            if c > 3:
                break
            c = c + 1

        C.ajouter_arete(v,parc[ran],None,'')
        retArr.append([v,parc[ran]])
        pon = sorted(map(sorted,ponts(C)))
        pass
    
    def copie_graphe(G : Graphe):
        C = Graphe()
        C.ajouter_sommets(G.sommets())
        C.ajouter_aretes(G.aretes())
        return C

    def tour_boucle():
        nonlocal pon, index, G, retArr
        C = copie_graphe(G)
        for p in pon:
            for j in p:
                if(len(pon) != 0):
                    if index == 0:
                        amelioration(C,p[0],p[1])
                        index = 1
                    else:
                        amelioration(C,p[1],p[0])
                        index = 0
    
    
    tour_boucle()
    counter = 0
    lastArr = []
    for i in retArr:
            lastArr.append(i)

    while counter <= 10:
        if len(retArr) < len(lastArr):
            lastArr = []
            for i in retArr:
                lastArr.append(i)
        retArr = []
        pon = sorted(map(sorted,ponts(G)))
        random()
        tour_boucle()
        counter = counter + 1
    

    return lastArr
    pass

def amelioration_points_aux(G : Graphe):
    tuple = numerotations(G)
    debut = tuple[0]
    parent = tuple[1]
    ancetre = tuple[2]
    articulation = points_articulation(G)

    def sort_articulation(debut,articulation):
        dic = dict()
        listRet = []
        for ar in articulation:
            dic[debut[ar]] = ar
        
        sortList = sorted(dic)
        retList = []
        for i in sortList:
            retList.append(dic[i])

        return retList
        
    sort = list(reversed(sort_articulation(debut,articulation)))
    articulation = sort
 
    eliminerPointRacine = []
    relierARacine = []
    descRacine = []

    def trouver_racine(parent):
        for p in parent:
            if parent[p] == None:
                return p
        return None

    racine = trouver_racine(parent)
    #print("La racine trouve: ", racine)

    for art in articulation:
        #Gestion de la racine
        if art in  parent: 
            if parent[art] == None:
                for p in parent:
                    if parent[p] == art:
                        descRacine.append(p)
                #print("Descendants de la racine: ",descRacine)
                if len(descRacine) >= 2:
                    eliminerPointRacine.append([descRacine[0],descRacine[1]])
                    #print("Arete rajouter pour elimine le point de la racine: ", descRacine[0], ",", descRacine[1])
        
        #Gestion des autres points
        for p in parent:
            par = parent[p]
            fils = p
            if par == art and fils not in articulation: # Si un sommet est le fils du point

                ancetreFils = ancetre[fils]
                if ancetreFils != ancetre[par]:
                    relierARacine.append(fils)
                else: #On regarde si il y a de la concurence
                    desc = []
                    for f in parent:
                        if parent[f] == par:
                            desc.append(f)
                            
                    if len(desc) == 1:
                        relierARacine.append(desc[0])
        
    #On enleve les descandant de la racine des sommet a relier a racine
    for d in descRacine:
        if d in relierARacine:
            relierARacine.pop(relierARacine.index(d))

    ret = []

    for s in relierARacine:
        ret.append([s,racine])
    
    for a in eliminerPointRacine:
        ret.append(a)


    #print("Sommets a rajouter a la racine: ", relierARacine)
                

    return ret
    pass

def amelioration_points_articulation(G : Graphe):
    C = Graphe()
    C.ajouter_sommets(G.sommets())
    C.ajouter_aretes(G.aretes())
    amelioreList = []

    while len(amelioration_points_aux(C)) != 0:
        res = amelioration_points_aux(C)
        #print(res)
        if(len(res) >= 1):
            u = res[0][0]
            v = res[0][1]
            amelioreList.append([u,v])
            C.ajouter_arete(u,v,None)
    
    return amelioreList
    pass

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--metro",nargs="*")
    parser.add_argument("--rer",nargs="*")
    parser.add_argument("--liste-stations",action="store_true")
    parser.add_argument("--ponts",action="store_true")
    parser.add_argument("--articulations",action="store_true")
    parser.add_argument("--ameliorer-ponts",action="store_true")
    parser.add_argument("--ameliorer-articulations",action="store_true")
    args = parser.parse_args()
    #print(args)

    reseau = Graphe()
    if args.metro != None and len(args.metro) != 0:
        for metro in args.metro:
            nomDuFichier = "METRO_" + metro + ".txt"
            charger_donnees(reseau,nomDuFichier)

    elif args.metro != None:
        metros = ['1','2','3','3b','4','5','6','7','7b','8','9','10','11','12','13','14']
        for metro in metros:
            nomDuFichier = "METRO_" + metro + ".txt"
            charger_donnees(reseau,nomDuFichier)

    if args.rer != None and len(args.rer) != 0 :
        for rer in args.rer:
            nomDuFichier = "RER_" + rer + ".txt"
            charger_donnees(reseau,nomDuFichier)
    elif args.rer != None:
        rers = ['A','B']
        for rer in rers:
            nomDuFichier = "RER_" + rer + ".txt"
            charger_donnees(reseau,nomDuFichier)
    
    if args.liste_stations == True:
        print("\nLe reseau contient les ", len(reseau.sommets()), " stations suivantes:\n")
        stations = sorted(map(reseau.nom_sommet, reseau.sommets()))
        for s in stations:
            print(s)

    if args.ponts == True:
        p = sorted(ponts(reseau))
        print("\nLe reseau contient les ",len(p)," ponts suivants:")
        for u,v in p:
            print("- ",reseau.nom_sommet(u)," -- ",reseau.nom_sommet(v))
    
    if args.articulations == True:
        a = sorted(points_articulation(reseau))
        print("\nLe reseau contient les ",len(a)," points d'articulation suivants:")
        count = 1
        for s in a:
            print(count," : ",reseau.nom_sommet(s))
            count = count + 1
    
    if args.ameliorer_ponts == True:
        ap = sorted(amelioration_ponts(reseau))
        print("\nOn peut eliminer tous les ponts du reseau en rajoutant les ",len(ap), " aretes suivantes:")
        for u,v in ap:
            print("- ",reseau.nom_sommet(u)," -- ", reseau.nom_sommet(v))
    
    if args.ameliorer_articulations == True:
        ar = sorted(amelioration_points_articulation(reseau))
        print("\nOn peut eliminer tous les points d'articulation du reseau en rajoutant les ",len(ar), " aretes suivantes:")
        for u,v in ar:
            print("- ",reseau.nom_sommet(u)," -- ", reseau.nom_sommet(v))
            

    # reseau = Graphe()
    # charger_donnees(reseau, "METRO_14.txt")
    # print(sorted(reseau.sommets()))
    # print(sorted(map(reseau.nom_sommet, reseau.sommets())))
    # print(sorted(reseau.aretes()))
    # charger_donnees(reseau, "METRO_3b.txt")
    # print(reseau.aretes())
    #doctest.testfile("tests/doctest_charger_donnees.txt")


    # G = Graphe()
    # G.ajouter_sommets(zip('abcdefghijkl', [None] * 12))
    # G.ajouter_aretes(
    # [('a', 'b', None), ('b', 'c', None), ('c', 'a', None), ('c', 'd', None), ('d', 'e', None),
    # ('e', 'f', None), ('f', 'd', None), ('a', 'g', None), ('g', 'h', None), ('h', 'a', None),
    # ('h', 'i', None), ('i', 'j', None), ('j', 'h', None), ('j', 'k', None), ('k', 'i', None),
    # ('i', 'l', None), ('k', 'h', None)])
    
    # print(G.sommets())
    #print(G.aretes())
    #print("Dico",G.dictionnaire)

    # # zipo = zip('abcdefghijkl', [None] * 12)
    # # print(tuple(zipo))

    # numer = numerotations(G)
    # print("Debut:\n",numer[0],"\n")
    # print("Parent:\n",numer[1],"\n")
    # print("Ancetre:\n",numer[2],"\n")
    # print("Articulations:\n",sorted(points_articulation(G)))
    # print("\n")

    #print("Ponts:",ponts(G))

    # print("Ponts:",sorted(map(sorted,ponts(G))))
    # res = amelioration_ponts(G)
    # print("Aretes a rajouter",res)
    # for u, v in res:
    #    G.ajouter_arete(u, v, None)
    # print("Pont restant:",sorted(map(sorted,ponts(G))))
    
    # res = amelioration_points_articulation(G)
    # print("\n")
    # print("Aretes a rajouter pour eliminer les points:",res)
    # for u, v in res:
    #     G.ajouter_arete(u, v, None)
    # print("Points d'articulation restants: ",len(points_articulation(G)))
    # print(points_articulation(G))

    # tabTest = amelioration_points_articulation(G)
    # print("Points a supprimer:",points_articulation(G))
    # print("Aretes a rajouter:",tabTest)
    # for u, v in tabTest:
    #      G.ajouter_arete(u, v, None)
    # print("Points articulation restant:",len(points_articulation(G)))

    # reseau = Graphe()
    # charger_donnees(reseau, "METRO_14.txt")

    # print("Ponts du metro:",ponts(reseau))
    # print("Aretes a rajouter:",amelioration_ponts(reseau))

    # for u,v in amelioration_ponts(reseau):
    #     reseau.ajouter_arete(u,v, None,"METRO_14")
    #print("Ponts du metro apres amelioration:",ponts(reseau))

    # print("Articulation du metro:",points_articulation(reseau))
    # print("Aretes a rajouter:",amelioration_points_articulation(reseau))

    # for u,v in amelioration_points_articulation(reseau):
    #     reseau.ajouter_arete(u,v, None,"METRO_14")
    #print("Articulation du metro apres amelioration:",points_articulation(reseau))

    pass

if __name__ == "__main__":
    main()
