"""
Project main launcher - load parameters and run the evolution.
Edit config.py then run: python src/launcher.py
"""

import sys
import os
import glob
import shutil

# Add the src directory to the Python path.
sys.path.insert(0, os.path.dirname(__file__))

# Import configuration.
import config

# Import project modules.
import readData
from main import evolution, VERBOSE_LOGS as _, info_log, debug_log


def _apply_runtime_config():
    """Inject config hyperparameters into runtime modules."""
    import main
    import tree

    main.MAX_GENERATIONS = config.MAX_GENERATIONS
    main.VERBOSE_LOGS = config.VERBOSE_LOGS
    main.CROSSOVER_PROB = config.CROSSOVER_PROB
    main.INIT_MIN_DEPTH = config.INIT_MIN_DEPTH
    main.INIT_MAX_DEPTH = config.INIT_MAX_DEPTH

    tree.MUTATE_PROB = config.MUTATE_PROB
    tree.LAMBDA_SIZE = config.LAMBDA_SIZE
    tree.MAX_TREE_DEPTH = config.MAX_TREE_DEPTH


def _run_one_dataset(relative_dataset_path):
    """Run the evolution on one dataset, then save a unique plot."""
    data_path = os.path.join(os.path.dirname(__file__), '..', relative_dataset_path)

    try:
        data = readData.parse_data(data_path)
        info_log(f'Data loaded: {data_path} | Points: {len(data)}')
    except FileNotFoundError:
        print(f"\nERROR: File not found: {data_path}")
        return False
    except Exception as e:
        print(f"\nERROR while loading data: {e}")
        return False

    info_log('Starting evolution...\n')
    gen_size = config.POPULATION_SIZE
    details = (1, config.TOURNAMENT_SIZE)

    evolution(
        data,
        gen_size,
        details,
        config.TOLERANCE,
        config.MAX_GENERATIONS,
    )

    # main.evolution always writes plots/plot3.png, so duplicate it with a unique name.
    plots_dir = os.path.join(os.path.dirname(__file__), '..', 'plots')
    plot_source = os.path.join(plots_dir, 'plot3.png')
    dataset_base = os.path.splitext(os.path.basename(relative_dataset_path))[0]
    plot_suffix = str(getattr(config, 'PLOT_SUFFIX', '')).strip()
    suffix_part = f'_{plot_suffix}' if plot_suffix else ''
    plot_target = os.path.join(plots_dir, f'plot_{dataset_base}{suffix_part}.png')

    if os.path.exists(plot_source):
        shutil.copyfile(plot_source, plot_target)
        info_log('plot copied:', plot_target)
        return True

    info_log('plot missing (no copy created for this dataset).')
    return False


def _list_txt_datasets():
    """Return all .txt datasets from data/, sorted alphabetically."""
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    files = sorted(glob.glob(os.path.join(data_dir, '*.txt')))
    return [os.path.relpath(path, os.path.join(os.path.dirname(__file__), '..')) for path in files]


def display_config():
    """Display the current configuration cleanly."""
    print("\n" + "="*60)
    print(" CURRENT CONFIGURATION")
    print("="*60)
    print(f"Max generations: {config.MAX_GENERATIONS}")
    print(f"Population: {config.POPULATION_SIZE}")
    print(f"Crossover: {config.CROSSOVER_PROB} | Mutation: {config.MUTATE_PROB}")
    print(f"Initial depth: {config.INIT_MIN_DEPTH}-{config.INIT_MAX_DEPTH}")
    print(f"Data file: {config.DATA_FILE}")
    print(f"Plot suffix: {config.PLOT_SUFFIX or '(none)'}")
    print(f"Detailed logs: {config.VERBOSE_LOGS}")
    print("="*60 + "\n")


def run_pipeline():
    """Run the evolution pipeline."""
    _apply_runtime_config()

    if getattr(config, 'RUN_ALL_DATASETS', False):
        datasets = _list_txt_datasets()
        if not datasets:
            print('\nERROR: No .txt dataset found in data/.')
            return

        print(f"\nBatch mode enabled: {len(datasets)} dataset(s) found.")
        success = 0
        for index, dataset in enumerate(datasets, start=1):
            print('\n' + '-' * 70)
            print(f"[{index}/{len(datasets)}] Dataset: {dataset}")
            print('-' * 70)
            ok = _run_one_dataset(dataset)
            if ok:
                success += 1

        print('\n' + '=' * 70)
        print(f"Batch finished: {success}/{len(datasets)} plot(s) copied to plots/.")
        print('=' * 70)
        return

    _run_one_dataset(config.DATA_FILE)

if __name__ == "__main__":
    display_config()
    run_pipeline()
