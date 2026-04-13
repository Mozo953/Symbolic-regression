# ---- DATA ----
DATA_FILE = "data/sr_poly_04.txt"
RUN_ALL_DATASETS = True  # True: run every .txt file in data/



# ---- EVOLUTION ----
MAX_GENERATIONS = 80   # Diversity
POPULATION_SIZE = 300    # Diversity
CROSSOVER_PROB = 0.95    # Slides: recombination should dominate variation
MUTATE_PROB = 0.05       # Slides: mutation should stay low overall
TOURNAMENT_SIZE = 2      # Slides: 2-tournament is the default example

# ---- INITIAL TREES ----
INIT_MIN_DEPTH = 2   # Complexity
INIT_MAX_DEPTH = 5   # Complexity
MAX_TREE_DEPTH = 6  # Complexity

# ---- CONSTANTS AND VARIABLES ----
CONST_MIN = -10
CONST_MAX = 10
CONST_PROB = 0.3
X_PROB = 0.4
POW_MIN_EXP = 2
POW_MAX_EXP = 3 # Complexity
 
# ---- FITNESS AND PENALTIES ----

LAMBDA_SIZE = 2e-4 # Lower = more complex


TOLERANCE = 0.001 # Stopping condition





################################################""
# Other
#SIZE_PENALTY_COEFF = 0.1  # No longer used; LAMBDA_SIZE penalizes complexity instead.
FITNESS_INVALID_PENALTY = 1e6  # Roughly: if invalid, apply a near-infinite penalty.
# ---- DISPLAY ----
VERBOSE_LOGS = False
PLOT_SUFFIX = ""  # Optional suffix added to copied plot filenames
DIV_ZERO_EPS = 1e-12
