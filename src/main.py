import tree as Tree  # import the tree module
import readData  # import the data loading module
from random import *  # import random functions
from heapq import heappush, heappop  # import min-heap operations
import copy  # import deep-copy support
import math  # import mathematical functions
import os  # build robust paths to datasets
import visualisation  # module dedicated to plotting results

# Next to do: refine mutation and debug.
VERBOSE_LOGS = False  # set to True to restore detailed logs
CROSSOVER_PROB = 0.9  # recommended crossover probability (0.7 to 0.9)
INIT_MIN_DEPTH = 2  # recommended initial minimum depth
INIT_MAX_DEPTH = 5  # recommended initial maximum depth
MAX_GENERATIONS = 100  # recommended maximum generations (100 to 300)
def info_log(*args):
    print(*args)
def debug_log(*args):
    if VERBOSE_LOGS:
        print(*args)


def tree_to_expression(node):
    if node is None:
        return '0'
    if node.left is None and node.right is None:
        return str(node.value)
    left_expr = tree_to_expression(node.left)
    right_expr = tree_to_expression(node.right)
    return f"({left_expr} {node.value} {right_expr})"

##########################START OF CODE##################################################################################




# Evolution function: drive the whole evolutionary cycle generation by generation.
def evolution(data, gen_size, details, tol, max_generations=MAX_GENERATIONS):  # run the full evolution
    

    kings = []  # store the best individuals encountered in a heap
    converged = False  # indicates whether the process should stop
    # simulate generations of natural selection
    converg_count = 0  # count generations without improvement
    gen_count = 0  # count the total number of generations




    # create the starting population
    info_log('Starting evolution')
    info_log('Parameters -> population:', gen_size, '| details:', details, '| tolerance:', tol)
    info_log('Creating the initial generation...')
    original = initial_generation(gen_size, data, INIT_MIN_DEPTH, INIT_MAX_DEPTH)  # create the first generation
    info_log('Initial generation ready. Initial fitness:', original[1].fitness)

    heappush(kings, original[1])  # add the first king to the heap

    old_gen = original  # define the current generation


    while not converged:  # main evolution loop
        if gen_count >= max_generations:
            converged = True
            info_log('Stop: maximum number of generations reached (', max_generations, ').')
            break

        if kings[0].fitness < tol:  # stopping condition on tolerance
            converged = True  # mark convergence
            info_log('Stop: tolerance reached after', gen_count, 'generation(s).')
            debug_log('Best individual tree (tolerance reached):')
            if VERBOSE_LOGS:
                kings[0].root.display()  # display the best tree structure
            break  # exit the loop

        best_before = kings[0].fitness  # historical best before this generation

        gen_count += 1  # increment the generation counter
        next_gen = run_generation(old_gen, details, data)  # generate the next population
        king = next_gen[1]  # get the best individual of the new generation

        try:  # try to add the new king to the heap
            heappush(kings, king)  # push the king into the priority structure
        except:  # catch a possible comparison problem
            print(' tie break error')  # tie-break error log
            continue  # move on to the next generation

        # age the population
        old_gen = next_gen  # the new generation becomes the current generation

        # display the best individuals
        info_log(
            f"Generation {gen_count:>3} | best in generation: {king.fitness:.6g} | "
            f"best so far: {kings[0].fitness:.6g}"
        )
        debug_log('Global best tree:')
        if VERBOSE_LOGS:
            kings[0].root.display()  # display the tree of the global best
            debug_log('Generation best tree:')
            king.root.display()  # display the tree of the local best

        # if we do not strictly improve, count stagnation (plateaus included)
        if king.fitness < best_before:
            converg_count = 0  # real strict improvement
        else:
            converg_count += 1
            if converg_count == 25:  # stagnation threshold
                info_log('Stop: stagnation (no improvement for 25 generations).')
                converged = True

    # final plot: dataset points + best function found
    plot_path = os.path.join(os.path.dirname(__file__), '..', 'plots', 'plot3.png')
    saved_path = visualisation.plot_points_and_functions(
        data,
        [kings[0]],
        ['best function'],
        plot_path,
    )
    if saved_path is not None:
        info_log('plot saved:', saved_path)
    else:
        # Avoid confusing an old plot with the current results.
        if os.path.exists(plot_path):
            os.remove(plot_path)
        info_log('plot not generated (matplotlib unavailable or plotting error).')

    if kings:
        stored_fitness = kings[0].fitness
        recomputed_fitness = kings[0].compute_fitness(data)
        fitness_delta = abs(recomputed_fitness - stored_fitness)
        info_log('final function:', tree_to_expression(kings[0].root))
        info_log('final fitness:', stored_fitness)
        info_log('recomputed final fitness:', recomputed_fitness, '| delta:', fitness_delta)

    # after debugging, run the real evolution
    # count = 0
    # continue until a new king goes below the tolerance
    # while (next_gen[1].fitness < tol and count < 10_000):
    #     next_gen = run_generation(next_gen, details, data)
    #     count += 1


# Roulette function: placeholder for future roulette selection.
def roulette_selection(old_gen, num_, data):  # function not implemented yet
    return  # immediate exit without processing


# Create a new generation from the old one.
def run_generation(old_gen, details, data):

    # details: tuple (selection mode, selection parameter)
    # details[0]: 1 for tournament, 2 for roulette
    # details[1]: tournament size for tournament mode


    next_gen = []  # will contain the next generation
    king = None  # store the best individual of the new generation

    ####################################################################################
    if details[0] == 1:  # TOURNAMENT
        previous_population = old_gen[0]
        population_size = len(previous_population)
        tournament_size = details[1]  # size of one tournament
        crossover_weight = max(0.0, float(CROSSOVER_PROB))
        mutation_weight = max(0.0, float(Tree.MUTATE_PROB))
        total_weight = crossover_weight + mutation_weight

        # Fitness of previous individuals: avoid unnecessary recomputation.
        for individual in previous_population:
            if not math.isfinite(individual.fitness):
                individual.compute_fitness(data)

        # 1) parent selection (tournaments) + creation of a full child population
        children = []
        target_children = population_size
        count = 0  # number of tournaments executed

        while len(children) < target_children:
            count += 1  # increment the tournament counter
            debug_log('running tournament', count)  # detailed log for the current tournament
            champions = tournament(previous_population, tournament_size, data)  # collect champions

            if len(champions) < 2:  # safety: not enough usable parents
                break





            for _ in range(len(champions)):
                if len(children) >= target_children:
                    break

                parent1, parent2 = sample(champions, 2)

                # Only one variation per child: crossover or mutation.
                if total_weight <= 0:
                    child = copy.deepcopy(parent1)
                elif random() < (crossover_weight / total_weight):
                    child = parent1.crossover(parent2)
                else:
                    child = copy.deepcopy(parent1)
                    child.mutate()
                child.compute_fitness(data)

                children.append(child)

        # 2) survivor selection: keep the best individuals
        # from the previous population and the children.
        candidates = previous_population + children
        survivors = sorted(candidates, key=lambda ind: ind.fitness)[:population_size]
        next_gen = [copy.deepcopy(ind) for ind in survivors]

        if survivors:
            king = copy.deepcopy(survivors[0])
     


    ####################################################################################
    if details[0] == 2:  # ROULETTE (not implemented yet)
        champions = roulette_selection(old_gen[0], details[1], data)  # call roulette placeholder



    ####################################################################################
    debug_log('size of the old generation is', len(old_gen[0]))
    debug_log('size of the new generation is', len(next_gen))
    return next_gen, king  # return the new generation and its best individual


# Initial population generation (ramped half-and-half).
def initial_generation(size, data, min_depth=2, max_depth=6):
    forest = []  # list of all population trees
    best_fitness = float('inf')  # best fitness value observed
    king = None  # current best individual

    # edge case: zero or negative size
    if size <= 0:
        return forest, king

    # clamp requested depths
    min_depth = max(1, int(min_depth))
    max_depth = max(1, int(max_depth))
    if min_depth > max_depth:
        min_depth, max_depth = max_depth, min_depth

    # Ramped half-and-half configurations: each depth in full mode then grow mode.
    configurations = []
    for depth in range(min_depth, max_depth + 1):
        configurations.append((depth, 'full'))
        configurations.append((depth, 'grow'))

    # Spread individuals as uniformly as possible across configurations.
    base = size // len(configurations)
    remainder = size % len(configurations)

    # Create the population and track the best individual as before.
    for config_index, (depth, mode) in enumerate(configurations):
        quota = base + (1 if config_index < remainder else 0)
        for _ in range(quota):
            individual = Tree.Tree(max_depth=depth, mode=mode)
            individual.compute_fitness(data)
            forest.append(individual)

            if individual.fitness < best_fitness:
                best_fitness = individual.fitness
                king = copy.deepcopy(individual)

    # Safety net: complete cleanly if some individuals are missing.
    while len(forest) < size:
        individual = Tree.Tree(max_depth=max_depth, mode='grow')
        individual.compute_fitness(data)
        forest.append(individual)

        if individual.fitness < best_fitness:
            best_fitness = individual.fitness
            king = copy.deepcopy(individual)

    return forest, king  # return the initial population and its king


# Tournament function: select champions through small random tournaments.
def tournament(pop, tournament_size, data):  # apply tournament selection
    champions = []  # store tournament winners

    if not pop:
        return champions

    tournament_size = max(1, min(int(tournament_size), len(pop)))
    num_tournaments = max(2, len(pop) // tournament_size)

    # Run small random tournaments and keep one champion per tournament.
    for _ in range(num_tournaments):
        group = sample(pop, tournament_size)
        best = float('inf')
        best_tree = None

        for individual in group:
            if math.isfinite(individual.fitness):
                fitness = individual.fitness
            else:
                fitness = individual.compute_fitness(data)

            if fitness < best:
                best = fitness
                best_tree = copy.deepcopy(individual)

        if best_tree is not None:
            champions.append(best_tree)

    return champions  # return the final list of champions




##########################END OF CODE######################################################################################

if __name__ == '__main__':
    info_log('Reading dataset...')
    file_to_load = os.path.join(os.path.dirname(__file__), '..', 'data', 'sr_periodic_02.txt')  # build the dataset path
    data = readData.parse_data(file_to_load)  # load data from disk
    info_log('Dataset loaded:', file_to_load, '| points:', len(data))

    gen_size = 200
    details = (1, 3)
    tolerance_threshold = 0.001
    evolution(data, gen_size, details, tolerance_threshold, MAX_GENERATIONS)  # run the evolution
