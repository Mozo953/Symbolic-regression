# Symbolic Regression

This project uses genetic programming to find symbolic expressions that fit a dataset.

The code builds expression trees, evaluates them on input data, and evolves a population of trees over several generations.

## Files

- `src/launcher.py`: main entry point
- `src/config.py`: parameters for the run
- `src/main.py`: evolutionary loop
- `src/tree.py`: tree representation and tree operators
- `src/node.py`: node representation
- `data/`: input datasets
- `plots/`: output plots

## How to run

1. Open `src/config.py`.
2. Set the dataset and the parameters you want to use.
3. Run:

```bash
python src/launcher.py
```

The launcher prints the active configuration, loads the data, runs the evolution, and saves plots in `plots/`.

## Main parameters

The most useful parameters in `src/config.py` are:

- `DATA_FILE`: dataset to run
- `RUN_ALL_DATASETS`: if `True`, runs every dataset in `data/`
- `PLOT_SUFFIX`: optional suffix added to copied plot filenames
- `POPULATION_SIZE`: number of individuals in each generation
- `MAX_GENERATIONS`: maximum number of generations
- `TOURNAMENT_SIZE`: tournament size for parent selection
- `CROSSOVER_PROB`: weight for crossover in the variation step
- `MUTATE_PROB`: weight for mutation in the variation step
- `INIT_MIN_DEPTH` and `INIT_MAX_DEPTH`: depth range for the initial population
- `MAX_TREE_DEPTH`: depth limit used during mutation
- `LAMBDA_SIZE`: size penalty in the fitness
- `TOLERANCE`: stopping threshold

## Data format

Each dataset is a text file.

- The first line is the number of points.
- Each following line contains one `x y` pair.

## Notes

- Run `src/launcher.py` if you want the values from `src/config.py` to be applied.
- `src/main.py` can still be run directly, but it uses its own local defaults.
- If `matplotlib` is not installed, the algorithm still runs, but plots are not generated.
