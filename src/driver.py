import tree as Tree
import data 
from random import *
from heapq import heappush, heappop
import copy
import math

# a faire ensuite : peaufiner la mutation et debugguer


## programme principal
## population + liste de listes pour les donnees d'entrainement
def evolution(data, gen_size, details, tol):
    """
    :param data: jeu de donnees d'entrainement, liste de tuples entree/sortie
    :param gen_size: taille de chaque generation (peut changer)
    :param details: tuple qui decrit le type de selection (1 = tournoi),
    et pour le tournoi, le nombre de tournois
    :param tol: seuil d'erreur sous lequel on considere que c'est bon
    """
    # tolérance d'erreur
    kings = []
    converged = False
    # on cree la population de depart
    print ('making original generation')
    original = new_gen(gen_size)
    print ('finished making original generation')

    heappush(kings, original[1])


    old_gen = original
    # on simule des generations de selection naturelle
    converg_count = 0
    gen_count = 0
    while not converged:
        if kings[0].fitness < tol:
            converged = True
            print("Error below tolerance, sucess! Printing king")
            king.root.afficher()
            print("Broke tolerance after ", gen_count, " generations")
            break


        gen_count += 1
        print ('generation', gen_count, ' completed, creating', ' generation...', gen_count + 1)
        next_gen = run_generation(old_gen, details, data)
        king = next_gen[1]
        print ('most fit individual from generation ', gen_count, ' has fitness', king.fitness)

        try:
            heappush(kings, king)
        except:
            print (' tie break error')
            continue

        # on fait vieillir la population
        old_gen = next_gen

        # si on a atteint la tolérance

        print(" the most fit king so far has fitness ", kings[0].fitness)
        kings[0].root.afficher()
        print(" the most fit king from this generation has fitness ", king.fitness)
        king.root.afficher()
        # si on n'ameliore pas plusieurs fois d'affilee, on stoppe
        # kings[0] = meilleur element du tas (min-heap)
        if king.fitness > kings[0].fitness:
            converg_count += 1
            if converg_count == 7:
                print('fitness has not improved in 7 generations, ending')
                converged = True
        else:
            converg_count = 0





    # apres debug, lancer la vraie evolution
    #count = 0
    # continuer jusqu'a ce qu'un nouveau king passe sous la tolerance
    # while (next_gen[1].fitness < tol and count < 10,000):
    #     next_gen = run_generation(next_gen, details, data)
    #     count += 1
    #


def roulette(old_gen, num_, data):
    return



def run_generation(old_gen, details, data):
    """

    :param old_gen: generation parent (index 0), avec le king en index 1
    :param details: tuple, premier entier = type de selection
    parentale (1 pour tournoi), deuxieme = nb de tournois
    :param data: jeu de donnees de test
    :return: tuple, entree 1 = nouvelle population (meme taille)
    entree 2 = meilleur arbre de la nouvelle generation
    """
    next_gen = []
    best_fitness = float('inf')
    king = None
    # on recupere la taille des tournois si mode tournoi
    if details[0] == 1:
        # on garde l'ancien king
        next_gen.append(old_gen[1])
        num_tourns = details[1]
        count = 0
        while(len(next_gen) < len(old_gen[0])):
            count += 1
            print ("running tournament ", count)
            champs = tournament(old_gen[0], num_tourns, data)
            # on recupere n enfants a partir d'un tournoi
            for i in range(num_tourns):
                # on tire 2 parents au hasard
                index1 = randint(0, len(champs) - 1)
                index2 = randint(0, len(champs) - 1)
                # pas de reproduction asexuee
                while index1 == index2:
                    index2 = randint(0, len(champs) - 1)
                # reproduction
                child = champs[index1].crossover(champs[index2])
                # mutation 5% du temps
                child.mutate(child.root)
                child.calcFitness(data)
                if child.fitness < best_fitness:
                    best_fitness = child.fitness
                    king = copy.deepcopy(child)
                next_gen.append(child)

                # 5% du temps, on ajoute un nouvel arbre
                if randint(0,100) < 5:
                    next_gen.append(Tree.Tree(10))
                #print ('enfant ', i, 'du tournoi ', count, ' a fitness', child.fitness)


    if details[0] == 2:
        champs = roulette(old_gen[0], details[1], data)


    print("size of the old generation is", len(old_gen[0]))
    print("size of new gen is", len(next_gen))
    return next_gen, king


def new_gen(size):
    """
    :type size: taille de la generation
    :return tuple: nouvelle generation en entree 1,
    meilleur individu en entree 2
    """
    forest = []
    best_fitness = float('inf')
    king = None
    ## on cree la population et on la classe par fitness
    for i in range(size):
        forest.append(Tree.Tree(15))
        # on calcule le fitness
        forest[i].calcFitness(data)
        if forest[i].fitness < best_fitness:
            best_fitness = forest[i].fitness
            king = copy.deepcopy(forest[i])
    return forest, king


def tournament(pop, num_torns, data):
    """
    on coupe la population en num_torn groupes (+1 pour les restes),
    puis on garde les meilleurs comme pool d'accouplement

    la liste pop doit deja etre melangee


    pour plus de complexite, on peut choisir pas seulement le meilleur,
    mais avec une proba p pour le 1er, p*(1-p) pour le 2e,
    p((1-p)^2) pour le 3e, etc.

    :param pop: population depuis laquelle on choisit le pool
    :param num_torns: nombre de tournois a lancer
    :param data: donnees pour evaluer le fitness
    :return champions: liste de champions (les plus fit)
    """
    champions = []
    # taille de chaque tournoi
    torn_size = int(len(pop) / num_torns)
    # torns = []

    # on cree les tournois et on en sort un gagnant a chaque fois
    for i in range(num_torns):
        # version avec 2e place (laissee en brouillon)
        # torns.append([])
        # on lance les tournois
        best = float('inf')
        best_tree = None
        for j in range(torn_size):
            fitness = pop[(i * torn_size) + j].calcFitness(data)
            # on verifie si c'est le meilleur
            if fitness < best:
                best = fitness
                best_tree = copy.deepcopy(pop[(i * torn_size) + j])
            # utile si tu veux garder le classement et donner une chance au 2e
            # torns[i].append(pop[(i * torn_size) + j])
        # meilleur final
        if best_tree is not None:
            champions.append(best_tree)
        else:
            print("No tree had a fitness better than infinity")
        print ("The tournament of size ", torn_size, "produced a champion of fitness: ", best)

    if len(pop) % num_torns != 0:
        # on ajoute les restes de la division entiere au dernier tournoi
        # a re-verifier au calme
        best = float('inf')
        best_tree = None
        for j in range(len(pop) % num_torns):
            fitness = pop[((num_torns - 1) * torn_size) + torn_size + j].calcFitness(data)
            if fitness < best:
                best = fitness
                best_tree = copy.deepcopy(pop[((num_torns - 1) * torn_size) + torn_size + j])
        if best_tree is not None:
            champions.append(best_tree)
        # torns.append([])
        # utile pour tester la chance de la 2e place
        # torns[num_torns].append(pop[((num_torns - 1) * torn_size) + torn_size + i])
    return champions


## tests
# Tree1 = Tree.Tree(5)
# Tree1.display_tree()

print ('reading data')
data = readData.readData('../data/dataset1.csv')
print ('done reading data')



# evolution avec ce dataset, 100 individus par generation,
# (selection par tournoi avec 15 tournois),
# et tolérance MSE de 1
gen_size = 100
evolution(data, gen_size, (1, int(math.sqrt(gen_size))), .1)
evo