"""
Lanceur principal du projet - charge les paramètres et lance l'évolution.
Modifiez config.py puis exécutez: python src/launcher.py
"""

import sys
import os
import glob
import shutil

# Ajoute le dossier src au chemin Python
sys.path.insert(0, os.path.dirname(__file__))

# Importe les configurations
import config

# Importe les modules du projet
import readData
from main import evolution, VERBOSE_LOGS as _, info_log, debug_log


def _appliquer_config_runtime():
    """Injecte les hyperparametres config dans les modules runtime."""
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


def _lancer_un_dataset(chemin_relatif_dataset):
    """Lance l'evolution pour un dataset puis sauvegarde un plot unique."""
    chemin_donnees = os.path.join(os.path.dirname(__file__), '..', chemin_relatif_dataset)

    try:
        data = readData.parse_data(chemin_donnees)
        info_log(f'Donnees chargees: {chemin_donnees} | Points: {len(data)}')
    except FileNotFoundError:
        print(f"\nERREUR: Fichier non trouve: {chemin_donnees}")
        return False
    except Exception as e:
        print(f"\nERREUR lors du chargement: {e}")
        return False

    info_log('Lancement de l\'evolution...\n')
    gen_size = config.POPULATION_SIZE
    details = (1, config.TOURNAMENT_SIZE)

    evolution(
        data,
        gen_size,
        details,
        config.TOLERANCE,
        config.MAX_GENERATIONS,
    )

    # main.evolution ecrit toujours plots/plot3.png, donc on le duplique avec un nom unique.
    plots_dir = os.path.join(os.path.dirname(__file__), '..', 'plots')
    plot_source = os.path.join(plots_dir, 'plot3.png')
    dataset_base = os.path.splitext(os.path.basename(chemin_relatif_dataset))[0]
    plot_suffix = str(getattr(config, 'PLOT_SUFFIX', '')).strip()
    suffix_part = f'_{plot_suffix}' if plot_suffix else ''
    plot_cible = os.path.join(plots_dir, f'plot_{dataset_base}{suffix_part}.png')

    if os.path.exists(plot_source):
        shutil.copyfile(plot_source, plot_cible)
        info_log('plot copie:', plot_cible)
        return True

    info_log('plot manquant (aucune copie pour ce dataset).')
    return False


def _lister_datasets_txt():
    """Retourne tous les datasets .txt du dossier data, tries alphabetiquement."""
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    fichiers = sorted(glob.glob(os.path.join(data_dir, '*.txt')))
    return [os.path.relpath(path, os.path.join(os.path.dirname(__file__), '..')) for path in fichiers]

def afficher_config():
    """Affiche la configuration actuelle proprement."""
    print("\n" + "="*60)
    print(" CONFIGURATION ACTUELLE")
    print("="*60)
    print(f"Max générations : {config.MAX_GENERATIONS}")
    print(f"Population : {config.POPULATION_SIZE}")
    print(f"Crossover : {config.CROSSOVER_PROB} | Mutation : {config.MUTATE_PROB}")
    print(f"Profondeur initiale : {config.INIT_MIN_DEPTH}-{config.INIT_MAX_DEPTH}")
    print(f"Fichier données : {config.DATA_FILE}")
    print(f"Suffixe plot : {config.PLOT_SUFFIX or '(none)'}")
    print(f"Logs détaillés : {config.VERBOSE_LOGS}")
    print("="*60 + "\n")

def lancer_pipeline():
    """Lance le pipeline d'évolution."""
    _appliquer_config_runtime()

    if getattr(config, 'RUN_ALL_DATASETS', False):
        datasets = _lister_datasets_txt()
        if not datasets:
            print('\nERREUR: Aucun dataset .txt trouve dans data/.')
            return

        print(f"\nMode batch actif: {len(datasets)} dataset(s) trouves.")
        succes = 0
        for index, dataset in enumerate(datasets, start=1):
            print('\n' + '-' * 70)
            print(f"[{index}/{len(datasets)}] Dataset: {dataset}")
            print('-' * 70)
            ok = _lancer_un_dataset(dataset)
            if ok:
                succes += 1

        print('\n' + '=' * 70)
        print(f"Batch termine: {succes}/{len(datasets)} plot(s) copies dans plots/.")
        print('=' * 70)
        return

    _lancer_un_dataset(config.DATA_FILE)

if __name__ == "__main__":
    afficher_config()
    lancer_pipeline()
