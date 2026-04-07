Architecture du projet de regression symbolique

1) Vision globale
Ce projet cherche a apprendre automatiquement une formule mathematique a partir de points (x, y).
La formule est representee comme un arbre binaire d'expression.
L'algorithme evolutif cree une population d'arbres, puis les fait evoluer generation apres generation.

2) Organisation des dossiers
Le dossier `data/` contient les jeux de donnees textes.
Le dossier `src/` contient toute la logique de modelisation (noeuds, arbres, evolution, lecture des donnees).

3) Role de `node.py`
`Node` est la brique de base de l'arbre.
Chaque noeud est soit un operateur (`+`, `-`, `*`, `/`), soit une valeur (`x` ou une constante entiere).

La methode `ajouter_enfants()` transforme une feuille en operateur et lui ajoute deux enfants numeriques.
Cela permet de faire grandir l'arbre progressivement.

Le fichier contient aussi `afficher()` pour visualiser l'arbre en ASCII.
C'est utile pour comprendre la forme des expressions produites.

4) Role de `tree.py`
`Tree` encapsule un arbre complet et ses metadonnees (`root`, `size`, `depth`, `fitness`).
Le constructeur construit un arbre aleatoire de taille cible via un parcours en largeur (BFS).

`evaluer()` et `evaluer_arbre()` calculent la sortie de l'expression pour une entree `x`.
La logique descend recursivement dans les sous-arbres, puis combine les resultats selon l'operateur.

`calculer_fitness(data)` mesure la qualite de l'arbre sur un dataset.
La metrique principale utilisee est la MSE (erreur quadratique moyenne).

`croiser(other)` fait le crossover genetique.
Le code choisit un chemin aleatoire dans chaque parent, puis echange les sous-arbres trouves.

`muter(root)` applique une mutation aleatoire (avec probabilite `MUTATE_PROB`).
Le but est d'introduire de la diversite pour eviter un blocage trop rapide de l'evolution.

5) Role de `main.py`
`main.py` pilote l'algorithme evolutif.
Il cree la population initiale, lance les generations, suit le meilleur individu (`king`) et decide quand arreter.

Fonctions importantes:
- `generation_initiale(size)`: cree la population initiale.
- `tournament(pop, num_torns, data)`: selection par tournois.
- `run_generation(old_gen, details, data)`: produit la generation suivante.
- `evolution(data, gen_size, details, tol)`: boucle principale jusqu'a convergence ou stagnation.

Le flux est simple:
1. Initialiser une population aleatoire.
2. Evaluer le fitness.
3. Selectionner des champions.
4. Reproduire (crossover) + muter.
5. Garder le meilleur et recommencer.

6) Role de `readData`
Le fichier `readData` contient `parse_data(file_path)`.
Le format attendu des fichiers de donnees est:
- ligne 1: nombre de points `n`
- lignes suivantes: deux flottants `x y`

La fonction retourne une liste de tuples `(x, y)`.

7) Comment les pieces s'emboitent
`main.py` demande des arbres a `tree.py`.
`tree.py` construit et manipule les arbres en s'appuyant sur `node.py`.
`readData` fournit les donnees d'entrainement pour calculer le fitness.

En resume: `Node` = unite locale, `Tree` = individu, `main` = evolution de la population.

8) Points de vigilance dans l'etat actuel
Le projet montre un melange de noms anglais/francais entre les fichiers.
Dans les versions precedentes, cela creait des decalages d'appels entre modules.

Ces points ont ete reparés dans la version actuelle (noms de fonctions alignes, lecture de donnees corrigee, ligne de debug supprimee).
Reste a surveiller la coherence des noms si de nouveaux refactors sont faits.

9) Lecture conseillee pour bien comprendre
Commence par `node.py` pour voir la structure minimale.
Passe ensuite a `tree.py` pour comprendre evaluation + fitness + operateurs genetiques.
Termine par `main.py` pour voir la boucle d'evolution complete.

Cette progression (noeud -> arbre -> population) rend l'architecture beaucoup plus facile a suivre.
