# ---- DONNEES ----
DATA_FILE = "data/sr_poly_04.txt"
RUN_ALL_DATASETS = True  # True: lance tous les .txt du dossier data/



# ---- EVOLUTION ---- 
MAX_GENERATIONS = 80   #Diversité
POPULATION_SIZE = 300    #Diversité
CROSSOVER_PROB = 0.95    # Slides: recombination should dominate variation
MUTATE_PROB = 0.05       # Slides: mutation should stay low overall
TOURNAMENT_SIZE = 2      # Slides: 2-tournament is the default example

# ---- ARBRES INITIAUX ----
INIT_MIN_DEPTH = 2   #complexité
INIT_MAX_DEPTH = 5   #complexité
MAX_TREE_DEPTH = 6  #complexité

# ---- CONSTANTES ET VARIABLES ----
CONST_MIN = -10
CONST_MAX = 10
CONST_PROB = 0.3
X_PROB = 0.4
POW_MIN_EXP = 2
POW_MAX_EXP = 3 #complexité
 
# ---- FITNESS ET PENALITES ----

LAMBDA_SIZE = 2e-4 #Bas = complexe


TOLERANCE = 0.001 #condition d'arrêt





################################################""
#Autre
#SIZE_PENALTY_COEFF = 0.1  #sert plus a rien, on utilise LAMBDA_SIZE a la place pour penaliser la complexite
FITNESS_INVALID_PENALTY = 1e6  #en gros si c invalide on met l'infini
# ---- AFFICHAGE ----
VERBOSE_LOGS = False
PLOT_SUFFIX = "new_tune"  # Optional suffix added to copied plot filenames
DIV_ZERO_EPS = 1e-12
