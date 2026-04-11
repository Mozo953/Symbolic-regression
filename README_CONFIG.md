# 🚀 Configuration Centralisée - Mode d'emploi

## Résumé
Vous avez maintenant **deux fichiers essentiels** pour contrôler tout le projet :

1. **`src/config.py`** - Tous les hyperparamètres
2. **`src/launcher.py`** - Lance le pipeline avec la config

## 📋 Comment utiliser

### Étape 1 : Ouvrir la configuration
Ouvrez **`src/config.py`** et modifiez ce que vous voulez :

```python
MAX_GENERATIONS = 100      # Augmentez pour plus de générations
POPULATION_SIZE = 50       # Taille de la population
MAX_TREE_DEPTH = 10        # Profondeur maximale des arbres
VERBOSE_LOGS = False       # Mettez à True pour voir les détails
```

### Étape 2 : Lancer
Terminal → exécutez :
```bash
python src/launcher.py
```

C'est tout ! La configuration s'affiche, puis l'évolution se lance.

## 🔧 Hyperparamètres importants

| Paramètre | Signification | Valeur défaut | Conseil |
|-----------|---|---|---|
| `MAX_GENERATIONS` | Nb de générations max | 100 | 100-300 pour tester |
| `POPULATION_SIZE` | Taille population | 50 | Plus gros = plus lent mais meilleur |
| `CROSSOVER_PROB` | Proba de croisement | 0.9 | 0.7-0.9 |
| `MUTATE_PROB` | Proba de mutation | 0.7 | 0.5-0.9 |
| `INIT_MIN_DEPTH` | Prof min initiale | 2 | 2-3 |
| `INIT_MAX_DEPTH` | Prof max initiale | 5 | 4-6 |
| `MAX_TREE_DEPTH` | Prof max globale | 10 | 6-12 |
| `DATA_FILE` | Fichier de données | "data/data.txt" | Voir dossier `data/` |
| `VERBOSE_LOGS` | Logs détaillés | False | True pour déboguer |

## 💡 Exemple : Tester vite avec une petite config

1. Ouvrez `src/config.py`
2. Modifiez :
```python
MAX_GENERATIONS = 10        # Très rapide pour tester
POPULATION_SIZE = 20        # Petit
```
3. Lancez : `python src/launcher.py`

## 💡 Exemple : Longue expérience

1. Ouvrez `src/config.py`
2. Modifiez :
```python
MAX_GENERATIONS = 500
POPULATION_SIZE = 200
MAX_TREE_DEPTH = 12
DATA_FILE = "data/sr_poly_01.txt"  # Changez le dataset
```
3. Lancez : `python src/launcher.py`

## ✅ Avantages du système

- ✅ **Un seul endroit** à modifier
- ✅ **Pas de risque** d'oublier une modification
- ✅ **Config affichée** avant lancement (confirmez avant de commencer)
- ✅ **Facile à lancer** : une simple command
- ✅ **Extensible** : ajouter un param = trivial

---

**Besoin d'aide ?** Les fichiers sont commentés, bon coding ! 🎯
