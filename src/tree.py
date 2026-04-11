from collections import deque
from node import *
from random import *
from readData import *
import math
import copy
MUTATE_PROB = 0.7
#SIZE_PENALTY_COEFF = 0.1
FITNESS_INVALID_PENALTY = 1e6
DIV_ZERO_EPS = 1e-12
LAMBDA_SIZE = 1e-5  # coefficient ajustable pour penaliser la complexite
MAX_TREE_DEPTH = 10  # profondeur max recommandee (6 a 8)
# a faire plus tard : ajouter d'autres variables




class Tree:
    # a ajuster plus tard pour eviter que tous les arbres aient
    # exactement la meme profondeur
    def __init__(self, size=15, max_depth=None, mode='full'):
        self.root = Node('num', 1)
        self.size = 1
        self.depth = 1
        self.fitness = float('inf')

        # Mode historique base sur la taille: comportement inchange pour les appels existants.
        if max_depth is None:
            target_size = max(1, int(size))
            # ici on utilise un parcours en largeur (BFS) pour trouver un noeud sans enfants
            frontier = deque([self.root])
            # on continue jusqu'a atteindre la taille voulue
            while self.size < target_size:
                next_node = frontier.popleft()
                if next_node.left is None and next_node.right is None:
                    next_node.ajouter_enfants()
                    self.size += 2
                    # on ajoute les nouveaux enfants
                    frontier.append(next_node.left)
                    frontier.append(next_node.right)
                    # on met a jour la profondeur
                    if next_node.left.depth > self.depth:
                        self.depth = next_node.left.depth
                else:
                    frontier.append(next_node.left)
                    frontier.append(next_node.right)
            return

        # Nouveau mode base sur la profondeur maximale (full/grow).
        target_depth = max(1, int(max_depth))
        mode = str(mode).lower()
        if mode not in ('full', 'grow'):
            raise ValueError('error, mode must be full or grow')

        self.root = self._generer_noeud(1, target_depth, mode)
        self.depth = self.mettre_a_jour_profondeur(self.root)
        self.size = self.mettre_a_jour_taille(self.root)

    def _generer_noeud(self, depth, max_depth, mode):
        # profondeur max atteinte: feuille numerique obligatoire
        if depth >= max_depth:
            return Node('num', depth)

        # mode full: tous les noeuds internes sont des operateurs
        if mode == 'full':
            noeud = Node('op', depth)
            noeud.left = self._generer_noeud(depth + 1, max_depth, mode)
            noeud.right = self._generer_noeud(depth + 1, max_depth, mode)
            return noeud

        # mode grow: on peut s'arreter plus tot, sauf a la racine
        if depth > 1 and random() < 0.5:   #ATTENTION, ca pourrait être un hp à regler. 
            return Node('num', depth)

        noeud = Node('op', depth)
        noeud.left = self._generer_noeud(depth + 1, max_depth, mode)
        noeud.right = self._generer_noeud(depth + 1, max_depth, mode)
        return noeud

    # pour comparer les arbres : egaux seulement si c'est la meme reference
    def __eq__(self, other):
        if self is other:
            return True
        else:
            return False

    # pour le tri : plus petit = meilleur fitness
    def __lt__(self, other):
        if self.fitness < other.fitness:
            return True
        else:
            return False






###########################FITNESS#########################
    # renvoie la valeur de l'arbre pour une entree x
    def evaluer(self, x):
        return self.evaluer_arbre(self.root, x)


    #Brique 1 : calcul fnotre f(x)
    def evaluer_arbre(self, node, x):
        # arbre vide
        if node is None:
            return 0

        # noeud feuille
        if node.left is None and node.right is None:
            if node.value=='x':
                return float(x)
            if isinstance(node.value, str) and node.value.startswith('x**'):
                try:
                    exp = int(node.value.split('**', 1)[1])
                except (IndexError, ValueError):
                    return None
                return float(x) ** exp
            if isinstance(node.value, (int, float)):
                return float(node.value)
            return None

        # on evalue le sous-arbre gauche
        left_sum = self.evaluer_arbre(node.left, x)

        # on evalue le sous-arbre droit
        right_sum = self.evaluer_arbre(node.right, x)
        if left_sum == None or right_sum == None:
            return None

        # on applique l'operation du noeud
        if node.value == '+':
            return float(left_sum + right_sum)

        elif node.value == '-':
            return float(left_sum - right_sum)

        elif node.value == '*':
            return float(left_sum * right_sum)

        elif node.value == '/':
            # TODO: remplacer plus tard par une vraie division protegee GP
            # (avec seuil/regularisation configurable) pour plus de stabilite.
            if abs(right_sum) > DIV_ZERO_EPS:
                return float(left_sum / right_sum)
            return float('inf')

        return None


    # calcul la taille de l'arbre pour pénaliser
    def taille_arbre(self, node):
        if node is None:
            return 0
        return 1 + self.taille_arbre(node.left) + self.taille_arbre(node.right)

    # calcule le fitness de l'arbre avec la pénalité
    def calculer_fitness(self, data):
        if not data:
            self.fitness = float('inf')
            return self.fitness

        # erreur quadratique moyenne sur tous les points
        sqrerr = 0.0
        invalid_count = 0
        for x, y in data:
            try:
                ans = self.evaluer(x)
                if ans is None:
                    invalid_count += 1
                    continue
                ans_val = float(ans)
            except Exception:
                invalid_count += 1
                continue

            if not math.isfinite(ans_val):
                invalid_count += 1
                continue

            sqrerr += (ans_val - y) ** 2

        # Aucun point evaluable: individu invalide.
        if invalid_count == len(data):
            self.fitness = float('inf')
            return self.fitness

        # Evite un fitness artificiellement faible si des points sont invalides.
        if invalid_count:
            sqrerr += FITNESS_INVALID_PENALTY * invalid_count

        mse = sqrerr / len(data)
        taille = self.taille_arbre(self.root)
        fitness = mse + LAMBDA_SIZE * taille    #Ici la pénalité TODO:mettre lambda en parametre
        self.fitness = fitness
        return fitness








###########################CROISEMENT#########################



    # croise deux arbres
    def croiser(self, other):
        # Crossover non destructif: on travaille sur des copies profondes.
        child = copy.deepcopy(self)
        donor = copy.deepcopy(other)

        # on choisit aleatoirement ou prelever/remplacer les sous-arbres
        self_path = child.chaine_bits_aleatoire(randint(1, child.depth))
        other_path = donor.chaine_bits_aleatoire(randint(1, donor.depth))

        # noeud cible dans l'enfant (et son parent)
        root1 = child.root
        parent1 = None
        direct1 = ''
        for bit in self_path:
            if bit == '0' and root1.left:
                parent1 = root1
                direct1 = 'l'
                root1 = root1.left
            elif bit == '1' and root1.right:
                parent1 = root1
                direct1 = 'r'
                root1 = root1.right

        # noeud donneur
        root2 = donor.root
        for bit in other_path:
            if bit == '0' and root2.left:
                root2 = root2.left
            elif bit == '1' and root2.right:
                root2 = root2.right

        graft = copy.deepcopy(root2)
        if parent1 is None:
            child.root = graft
        elif direct1 == 'l':
            parent1.left = graft
        elif direct1 == 'r':
            parent1.right = graft

        child.depth = child.mettre_a_jour_profondeur(child.root)
        child.size = child.mettre_a_jour_taille(child.root)
        child.fitness = float('inf')
        return child


#############################################################""

    # def getRootLength(self,root,root_length):
    #     print self.depth
    #     self.root.afficher()
    #     if root==None:
    #         return root_length
    #     return(max(self.getRootLength(root.left,root_length+1),
    #     self.getRootLength(root.right,root_length+1)))

    # algo recursif qui renvoie la profondeur de l'arbre
    def mettre_a_jour_profondeur(self, root, depth=0):
        if root == None:
            return depth
        depth += 1
        return max(self.mettre_a_jour_profondeur(root.right, depth),
        self.mettre_a_jour_profondeur(root.left, depth))

    # algo recursif qui met a jour la taille de l'arbre
    def mettre_a_jour_taille(self, root, size=0):
        if root == None:
            return 0
        return 1 + self.mettre_a_jour_taille(root.right, size) + self.mettre_a_jour_taille(root.left, size)





#############################MUTATION#####################################################
    # mutation de l'arbre, plutot vers le bas
    def muter(self, root):
        # 1) on decide si on mute ou non
        if random() >= MUTATE_PROB or root is None:
            return

        # 2) on choisit un chemin aleatoire, en visant un noeud hors racine
        current_depth = self.mettre_a_jour_profondeur(root)
        steps = randint(1, max(1, current_depth - 1))
        path = self.chaine_bits_aleatoire(steps)

        parent = None
        direct = ''
        node = root
        node_depth = 1

        for bit in path:
            if bit == '0' and node.left is not None:
                parent = node
                direct = 'l'
                node = node.left
                node_depth += 1
            elif bit == '1' and node.right is not None:
                parent = node
                direct = 'r'
                node = node.right
                node_depth += 1
            else:
                # chemin coupe: on s'arrete proprement au dernier noeud atteignable
                break

        # 3) si aucun parent valide, on tente un enfant direct de la racine
        if parent is None:
            candidats = []
            if root.left is not None:
                candidats.append('l')
            if root.right is not None:
                candidats.append('r')

            if not candidats:
                return

            direct = candidats[randint(0, len(candidats) - 1)]
            parent = root
            node_depth = 2

        # 4) generation d'un nouveau sous-arbre aleatoire (mode grow)
        borne_basse = node_depth + 1
        if borne_basse > MAX_TREE_DEPTH:
            return

        borne_haute = min(MAX_TREE_DEPTH, max(borne_basse, current_depth + 2))
        new_max_depth = randint(borne_basse, borne_haute)
        new_subtree = self._generer_noeud(node_depth, new_max_depth, 'grow')

        # 5) remplacement complet de l'ancien sous-arbre cible
        if direct == 'l':
            parent.left = new_subtree
        else:
            parent.right = new_subtree

        # 6) mise a jour des metadonnees apres mutation
        self.depth = self.mettre_a_jour_profondeur(self.root)
        self.size = self.mettre_a_jour_taille(self.root)
        self.fitness = float('inf')



    # sert a tirer un chemin binaire aleatoire dans l'arbre
    def chaine_bits_aleatoire(self, length):
        string=''
        for i in range(length):
            bit = randint(0, 1)
            string += str(bit)
        return string

