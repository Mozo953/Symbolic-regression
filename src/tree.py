from collections import deque
from node import *
from random import *
from readData import *
MUTATE_PROB = .05
SIZE_PENALTY_COEFF = .1
# a faire plus tard : ajouter d'autres variables

class Tree:
    # a ajuster plus tard pour eviter que tous les arbres aient
    # exactement la meme profondeur
    def __init__(self, size):
        self.root = Node('num', 1)
        self.size = 1
        self.depth = 1
        self.fitness = float('inf')

        # ici on utilise un parcours en largeur (BFS) pour trouver un noeud sans enfants
        frontier = deque([self.root])
        # on continue jusqu'a atteindre la taille voulue
        while self.size < size:
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

    # renvoie la valeur de l'arbre pour une entree x
    def evaluer(self, x):
        return self.evaluer_arbre(self.root, x)

    # petite fonction recursive qui calcule la sortie de l'arbre
    # pour une valeur x donnee
    #https://www.geeksforgeeks.org/evaluation-of-expression-tree/
    def evaluer_arbre(self, node, x):
        # arbre vide
        if node is None:
            return 0
        # si division par zero, on renvoie inf
        if node.value=='/' and node.right==0:
            print ("divided by zero")
            return float('inf')

        # noeud feuille
        if node.left is None and node.right is None:
            if node.value=='x':
                return float(x)
            else:
                return node.value

        # on evalue le sous-arbre gauche
        left_sum = self.evaluer_arbre(node.left, x)

        # on evalue le sous-arbre droit
        right_sum = self.evaluer_arbre(node.right, x)
        if left_sum ==None or right_sum==None:
            return None

        # on applique l'operation du noeud
        if node.value == '+':
            return float(left_sum + right_sum)

        elif node.value == '-':
            return float(left_sum - right_sum)

        elif node.value == '*':
            return float(left_sum * right_sum)

        else:
            if right_sum!=0:
                return float(left_sum / right_sum)
            else:
                return float('inf')

    # calcule le fitness de l'arbre
    # avec une petite penalite quand l'arbre devient trop gros
    def calculer_fitness(self, data):
        # erreur quadratique
        sqrerr = 0
        # on parcourt tous les points du dataset
        for row in range(len(data)):

            # garde-fou au cas ou l'evaluation renvoie None
            ans = self.evaluer(data[row][0])
            if ans !=None:
                sqrerr += (ans-data[row][1])**2
        mse = sqrerr/len(data)
        rmse= mse**(.5)
        # on ajoute la penalite de taille
        rmse+=SIZE_PENALTY_COEFF*self.size
        self.fitness = mse ### on peut changer avec rmse et voir surtout la dif donc je laisse mse mais a modifier e
        return mse

    # croise deux arbres
    def croiser(self, other):
        # on choisit aleatoirement ou faire le croisement
        selfPath = self.chaine_bits_aleatoire(randint(1, self.depth))
        otherPath = other.chaine_bits_aleatoire(randint(1, other.depth))


        # on trouve le noeud cote self
        root1 = self.root
        root_depth1 = 1
        for i in range(len(selfPath)):
            # si 0 on tente a gauche
            if selfPath[i] == '0' and root1.left:
                # on garde le parent
                parent1=root1
                direct1='l'
                root1 = root1.left
                root_depth1+=1
            # si 1 on tente a droite
            elif selfPath[i]=='1' and root1.right:
                # on garde le parent
                parent1=root1
                direct1='r'
                root1 = root1.right
                root_depth1+=1


        # on trouve le noeud cote other
        root2 = other.root
        root_depth2 = 1
        for i in range(len(otherPath)):
            # si 0 on tente a gauche
            if otherPath[i] == '0' and root2.left:
                # on garde le parent
                parent2=root2
                direct2='l'
                root2 = root2.left
                root_depth2+=1
            # si 1 on tente a droite
            elif otherPath[i]=='1' and root2.right:
                # on garde le parent
                parent2=root2
                direct2='r'
                root2 = root2.right
                root_depth2+=1

        # on echange les sous-arbres
        if direct1=='l':
            parent1.left=root2
        elif direct1=='r':
            parent1.right=root2
        else:
            print ('Did not crossover parent1')

        if direct2=='l':
            parent2.left=root1
        elif direct2=='r':
            parent2.right=root1
        else:
            print ('Did not crossover parent2')


        # on met a jour la profondeur/taille apres croisement
        #root_length1=self.getRootLength(root1,-1)
        #root_length2=self.getRootLength(root2,-1)
        #print (root_length1)
        #print (root_length2)
        # niveau racine + longueur
        #self.depth=self.mettre_a_jour_profondeur(self.root)
        other.depth = other.mettre_a_jour_profondeur(other.root)
        other.size = other.mettre_a_jour_taille(other.root)

        #new_tree = Tree(5)
        return other


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
            return size
        return self.mettre_a_jour_taille(root.right, size) + self.mettre_a_jour_taille(root.left, size)

    # mutation de l'arbre, plutot vers le bas
    def muter(self, root):
        if random.random() <  MUTATE_PROB:
        # on evite de muter trop pres de la racine
            # et on ne touche jamais la racine
            lower = max(1,self.depth-2) # p, acce^te pas la racaine
            path = self.chaine_bits_aleatoire(randint(lower, self.depth+2))
            direct=''
            depth = 1
            for i in range(len(path)):
                # si 0 on tente a gauche
                if path[i] == '0' and root.left:
                    # on garde le parent
                    parent=root
                    direct='l'
                    root = root.left
                    depth+=1

                # si 1 on tente a droite
                elif path[i]=='1' and root.right:
                    # on garde le parent
                    parent=root
                    direct='r'
                    root = root.right
                    depth+=1
            # une fois le noeud trouve, on le mute
            new_node = Node(root.type,depth)
            new_node.right=root.right
            new_node.left=root.left
            print (new_node.value)
            if direct=='l':
                parent.left=new_node
            elif direct=='r':
                parent.right=new_node



    # sert a tirer un chemin binaire aleatoire dans l'arbre
    def chaine_bits_aleatoire(self, length):
        string=''
        for i in range(length):
            bit = randint(0, 1)
            string += str(bit)
        return string


# ## tests rapides
# Tree1 = Tree(3)
# fitness = (Tree1.calculer_fitness(small_train1))