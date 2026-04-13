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
    def __init__(self, max_depth=1, mode='full'):
        # Construction des arbres uniquement par profondeur max en mode full/grow.
        target_depth = max(1, int(max_depth))
        mode = str(mode).lower()
        if mode not in ('full', 'grow'):
            raise ValueError('error, mode must be full or grow')

        self.fitness = float('inf')
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

    def _lister_noeuds(self, include_root=True):
        if self.root is None:
            return []

        noeuds = []
        pile = [(self.root, None, '', 1)]
        while pile:
            noeud, parent, direction, depth = pile.pop()
            if include_root or parent is not None:
                noeuds.append((noeud, parent, direction, depth))
            if noeud.right is not None:
                pile.append((noeud.right, noeud, 'r', depth + 1))
            if noeud.left is not None:
                pile.append((noeud.left, noeud, 'l', depth + 1))
        return noeuds

    def _mettre_a_jour_profondeurs_noeuds(self, node, depth=1):
        if node is None:
            return
        node.depth = depth
        self._mettre_a_jour_profondeurs_noeuds(node.left, depth + 1)
        self._mettre_a_jour_profondeurs_noeuds(node.right, depth + 1)

    def _mettre_a_jour_metadonnees(self):
        self._mettre_a_jour_profondeurs_noeuds(self.root)
        self.depth = self.mettre_a_jour_profondeur(self.root)
        self.size = self.mettre_a_jour_taille(self.root)
        self.fitness = float('inf')

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

        cibles = child._lister_noeuds(include_root=True)
        donneurs = donor._lister_noeuds(include_root=True)
        if not cibles or not donneurs:
            return child

        _, parent1, direct1, _ = choice(cibles)
        root2, _, _, _ = choice(donneurs)

        graft = copy.deepcopy(root2)
        if parent1 is None:
            child.root = graft
        elif direct1 == 'l':
            parent1.left = graft
        elif direct1 == 'r':
            parent1.right = graft

        child._mettre_a_jour_metadonnees()
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
    # mutation de l'arbre par remplacement uniforme d'un sous-arbre existant
    def muter(self, root=None):
        if root is None:
            root = self.root
        if root is None:
            return

        current_depth = self.mettre_a_jour_profondeur(root)
        candidats = self._lister_noeuds(include_root=True)
        if not candidats:
            return

        _, parent, direct, node_depth = choice(candidats)

        # generation d'un nouveau sous-arbre aleatoire (mode grow)
        borne_basse = node_depth + 1
        if borne_basse > MAX_TREE_DEPTH:
            return

        borne_haute = min(MAX_TREE_DEPTH, max(borne_basse, current_depth + 2))
        new_max_depth = randint(borne_basse, borne_haute)
        new_subtree = self._generer_noeud(node_depth, new_max_depth, 'grow')

        if parent is None:
            self.root = new_subtree
        elif direct == 'l':
            parent.left = new_subtree
        else:
            parent.right = new_subtree

        self._mettre_a_jour_metadonnees()
