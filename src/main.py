import tree as Tree  # importe le module des arbres
import readData  # importe le module de lecture des donnees
from random import *  # importe les fonctions aleatoires
from heapq import heappush, heappop  # importe les operations sur tas min-heap
import copy  # importe la copie profonde des objets
import math  # importe les fonctions mathematiques
import os  # construit des chemins robustes vers les datasets
import visualisation  # module dedie au tracage des resultats

# a faire ensuite : peaufiner la mutation et debugguer
VERBOSE_LOGS = False  # mettre a True pour retrouver les logs detailles
CROSSOVER_PROB = 0.9  # proba de crossover recommandee (0.7 a 0.9)
INIT_MIN_DEPTH = 2  # profondeur initiale min recommandee
INIT_MAX_DEPTH = 5  # profondeur initiale max recommandee
MAX_GENERATIONS = 100  # nombre max de generations recommande (100 a 300)
def info_log(*args):
    print(*args)
def debug_log(*args):
    if VERBOSE_LOGS:
        print(*args)
def arbre_en_expression(noeud):
    if noeud is None:
        return '0'
    if noeud.left is None and noeud.right is None:
        return str(noeud.value)
    gauche = arbre_en_expression(noeud.left)
    droite = arbre_en_expression(noeud.right)
    return f"({gauche} {noeud.value} {droite})"

##########################DEBUT CODE####################################################################################




# Fonction evolution : pilote tout le cycle evolutif generation par generation.
def evolution(data, gen_size, details, tol, max_generations=MAX_GENERATIONS):  # lance l'evolution complete
    

    kings = []  # stocke les meilleurs individus rencontres dans un tas
    converged = False  # indique si le processus doit s'arreter
    # on simule des generations de selection naturelle
    converg_count = 0  # compte le nombre de generations sans amelioration
    gen_count = 0  # compte le nombre total de generations




    # on cree la population de depart
    info_log('Demarrage evolution')
    info_log('Parametres -> population:', gen_size, '| details:', details, '| tolerance:', tol)
    info_log('Creation de la generation initiale...')
    original = generation_initiale(gen_size, data, INIT_MIN_DEPTH, INIT_MAX_DEPTH)  # cree la premiere generation
    info_log('Generation initiale prete. Fitness initiale:', original[1].fitness)

    heappush(kings, original[1])  # ajoute le premier king dans le tas

    old_gen = original  # definit la generation courante


    while not converged:  # boucle principale de l'evolution
        if gen_count >= max_generations:
            converged = True
            info_log('Arret: nombre maximal de generations atteint (', max_generations, ').')
            break

        if kings[0].fitness < tol:  # condition d'arret sur la tolerance
            converged = True  # marque la convergence
            info_log('Arret: tolerance atteinte apres', gen_count, 'generation(s).')
            debug_log('Arbre du meilleur individu (tolerance atteinte):')
            if VERBOSE_LOGS:
                kings[0].root.afficher()  # affiche la structure du meilleur arbre
            break  # sort de la boucle

        best_before = kings[0].fitness  # meilleur historique avant cette generation

        gen_count += 1  # incremente le compteur de generation
        next_gen = run_generation(old_gen, details, data)  # genere la population suivante
        king = next_gen[1]  # recupere le meilleur individu de la nouvelle generation

        try:  # tentative d'ajout du nouveau king dans le tas
            heappush(kings, king)  # pousse le king dans la structure de priorite
        except:  # capture un eventuel probleme de comparaison
            print(' tie break error')  # log d'erreur de tie-break
            continue  # passe a la generation suivante

        # on fait vieillir la population
        old_gen = next_gen  # la nouvelle generation devient la generation courante

        # affichage des meilleurs individus
        info_log(
            f"Generation {gen_count:>3} | meilleur dans la géné : {king.fitness:.6g} | "
            f"meilleur depuis le début: {kings[0].fitness:.6g}"
        )
        debug_log('Arbre meilleur global:')
        if VERBOSE_LOGS:
            kings[0].root.afficher()  # affiche l'arbre du meilleur global
            debug_log('Arbre meilleur de la generation:')
            king.root.afficher()  # affiche l'arbre du meilleur local

        # si on n'ameliore pas strictement, on compte de la stagnation (plateau inclus)
        if king.fitness < best_before:
            converg_count = 0  # vraie amelioration stricte
        else:
            converg_count += 1
            if converg_count == 25:  # seuil de stagnation
                info_log('Arret: stagnation (pas d\'amelioration sur 25 generations).')
                converged = True

    # plot final: points du dataset + meilleure fonction obtenue
    plot_path = os.path.join(os.path.dirname(__file__), '..', 'plots', 'plot3.png')
    saved_path = visualisation.tracer_points_et_fonctions(
        data,
        [kings[0]],
        ['meilleure fonction'],
        plot_path,
    )
    if saved_path is not None:
        info_log('plot sauvegarde:', saved_path)
    else:
        # Evite de confondre un ancien plot avec les resultats courants.
        if os.path.exists(plot_path):
            os.remove(plot_path)
        info_log('plot non genere (matplotlib indisponible ou erreur de trace).')

    if kings:
        fitness_stockee = kings[0].fitness
        fitness_recalculee = kings[0].calculer_fitness(data)
        delta_fitness = abs(fitness_recalculee - fitness_stockee)
        info_log('fonction finale:', arbre_en_expression(kings[0].root))
        info_log('fitness finale:', fitness_stockee)
        info_log('fitness finale recalculee:', fitness_recalculee, '| ecart:', delta_fitness)

    # apres debug, lancer la vraie evolution
    # count = 0
    # continuer jusqu'a ce qu'un nouveau king passe sous la tolerance
    # while (next_gen[1].fitness < tol and count < 10_000):
    #     next_gen = run_generation(next_gen, details, data)
    #     count += 1


# Fonction roulette : placeholder pour une future selection par roulette.
def roulette(old_gen, num_, data):  # fonction non implementee pour l'instant
    return  # sortie immediate sans traitement


# cree une nouvelle generation a partir de l'ancienne.
def run_generation(old_gen, details, data, elite_size=2):  

    #details : tuple (mode de selection, parametre de selection)
    #details[0] : 1 pour tournoi, 2 pour roulette
    #details[1] : taille d'un tournoi pour le mode tournoi


    next_gen = []  # contiendra la generation suivante (elites + enfants)
    best_fitness = float('inf')  # initialise le meilleur fitness observe
    king = None  # stocke le meilleur individu de la nouvelle generation

    ####################################################################################
    if details[0] == 1:  # SI ON FAIT UN TOURNOI
        population_prec = old_gen[0]
        elite_size = max(1, min(elite_size, len(population_prec)))
        tournament_size = details[1]  # taille d'un tournoi

        # Fitness des anciens individus: on evite les recalculs inutiles.
        for individu in population_prec:
            if not math.isfinite(individu.fitness):
                individu.calculer_fitness(data)

        # 1) selection des parents (tournois) + creation des enfants
        children = []
        target_children = max(0, len(population_prec) - elite_size)
        count = 0  # compteur de tournois executes

        while len(children) < target_children:
            count += 1  # incremente le compteur de tournoi
            debug_log('running tournament', count)  # log detaille du tournoi courant
            champs = tournament(population_prec, tournament_size, data)  # recupere les champions

            if len(champs) < 2:  # securite: pas assez de parents exploitables
                break





            # PARMI LES CHAMPIONS, ON FAIT LES PAIRES ET ON GENERE DES ENFANTS

            for i in range(len(champs)):  # cree des enfants depuis les champions
                index1 = randint(0, len(champs) - 1)  # tire le premier parent
                index2 = randint(0, len(champs) - 1)  # tire le second parent

                while index1 == index2:  # evite la reproduction asexuee: évite les doublons
                    index2 = randint(0, len(champs) - 1)  # retire un second parent

                # applique le crossover avec une proba explicite
                if random() < CROSSOVER_PROB:
                    child = champs[index1].croiser(champs[index2])  # CROSSOVER
                else:
                    child = copy.deepcopy(champs[index1])  # sinon on clone un parent
                child.muter(child.root)  # MUTATION
                child.calculer_fitness(data)  # CAUCLUL DU FITNESS

                children.append(child)  # ajoute l'enfant a la nouvelle generation

                if len(children) < target_children and randint(0, 100) < 5:  # injection aleatoire de diversite a 5%
                    random_depth = randint(INIT_MIN_DEPTH, INIT_MAX_DEPTH)
                    random_tree = Tree.Tree(max_depth=random_depth, mode='grow')
                    random_tree.calculer_fitness(data)
                    children.append(random_tree)

                if len(children) >= target_children:
                    break

        # 2) selection des survivants (elitisme + enfants uniquement)
        # Les enfants ont deja leur fitness, pas besoin de recalculer.
        children = children[:target_children]

        old_sorted = sorted(population_prec, key=lambda ind: ind.fitness)
        elites = [copy.deepcopy(ind) for ind in old_sorted[:elite_size]]

        # Apres elitisme, on remplit uniquement avec des enfants.
        next_gen = elites + children

        if next_gen:
            king = copy.deepcopy(min(next_gen, key=lambda ind: ind.fitness))
            best_fitness = king.fitness
     


    ####################################################################################
    if details[0] == 2:  # ROULETTE (pas encore fait)
        champs = roulette(old_gen[0], details[1], data)  # appel du placeholder roulette



    ####################################################################################
    debug_log('size of the old generation is', len(old_gen[0]))
    debug_log('size of new gen is', len(next_gen))
    return next_gen, king  # renvoie la nouvelle generation et son meilleur individu


# Generation de la population initiale (ramped half-and-half).
def generation_initiale(size, data, min_depth=2, max_depth=6):
    forest = []  # liste de tous les arbres de la population
    best_fitness = float('inf')  # meilleure valeur de fitness observee
    king = None  # meilleur individu courant

    # cas limite: taille nulle ou negative
    if size <= 0:
        return forest, king

    # securise les profondeurs demandees
    min_depth = max(1, int(min_depth))
    max_depth = max(1, int(max_depth))
    if min_depth > max_depth:
        min_depth, max_depth = max_depth, min_depth

    # configurations ramped half-and-half: chaque profondeur en mode full puis grow
    configurations = []
    for depth in range(min_depth, max_depth + 1):
        configurations.append((depth, 'full'))
        configurations.append((depth, 'grow'))

    # repartition la plus uniforme possible sur les configurations
    base = size // len(configurations)
    reste = size % len(configurations)

    # creation de la population et suivi du meilleur individu comme avant
    for index_cfg, (depth, mode) in enumerate(configurations):
        quota = base + (1 if index_cfg < reste else 0)
        for _ in range(quota):
            individu = Tree.Tree(max_depth=depth, mode=mode)
            individu.calculer_fitness(data)
            forest.append(individu)

            if individu.fitness < best_fitness:
                best_fitness = individu.fitness
                king = copy.deepcopy(individu)

    # filet de securite: complete proprement si jamais il manque des individus
    while len(forest) < size:
        individu = Tree.Tree(max_depth=max_depth, mode='grow')
        individu.calculer_fitness(data)
        forest.append(individu)

        if individu.fitness < best_fitness:
            best_fitness = individu.fitness
            king = copy.deepcopy(individu)

    return forest, king  # renvoie la population initiale et son roi


# Fonction tournament : selectionne des champions via petits tournois aleatoires.
def tournament(pop, tournament_size, data):  # applique une selection par tournois
    champions = []  # stocke les gagnants des tournois

    if not pop:
        return champions

    tournament_size = max(1, min(int(tournament_size), len(pop)))
    num_tournaments = max(2, len(pop) // tournament_size)

    # on lance des petits tournois aleatoires, et on garde un champion par tournoi
    for _ in range(num_tournaments):
        groupe = sample(pop, tournament_size)
        best = float('inf')
        best_tree = None

        for individu in groupe:
            if math.isfinite(individu.fitness):
                fitness = individu.fitness
            else:
                fitness = individu.calculer_fitness(data)

            if fitness < best:
                best = fitness
                best_tree = copy.deepcopy(individu)

        if best_tree is not None:
            champions.append(best_tree)

    return champions  # renvoie la liste finale des champions




##########################FIN CODE########################################################################################

info_log('Lecture du dataset...')
chargement_fichier = os.path.join(os.path.dirname(__file__), '..', 'data', 'sr_periodic_02.txt')  # construit le chemin du dataset
data = readData.parse_data(chargement_fichier)  # charge les donnees depuis le disque
info_log('Dataset charge:', chargement_fichier, '| points:', len(data))


gen_size = 200  
details = (1,3)  
seuil_tolerance = 0.001
evolution(data, gen_size, details, seuil_tolerance, MAX_GENERATIONS)  # lance l'evolution
