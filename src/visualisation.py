import math
import os


def _linspace(x_min, x_max, n):
    if n <= 1:
        return [x_min]
    step = (x_max - x_min) / (n - 1)
    return [x_min + i * step for i in range(n)]


def _courbe_arbre(arbre, xs):
    ys = []
    for x in xs:
        try:
            y = arbre.evaluer(x)
            if y is None or not math.isfinite(float(y)):
                ys.append(float("nan"))
            else:
                ys.append(float(y))
        except Exception:
            ys.append(float("nan"))
    return ys


def tracer_points_et_fonctions(data, arbres, labels=None, output_path=None):
    """Trace les points cibles + une ou plusieurs fonctions d'arbres sur le meme graphe."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as exc:
        print("Impossible de tracer (matplotlib indisponible):", exc)
        return None

    if not data:
        print("Aucune donnee a tracer.")
        return None

    if labels is None:
        labels = [f"fonction_{i + 1}" for i in range(len(arbres))]

    x_data = [p[0] for p in data]
    y_data = [p[1] for p in data]

    x_min = min(x_data)
    x_max = max(x_data)
    y_min = min(y_data)
    y_max = max(y_data)
    y_range = y_max - y_min
    if y_range == 0:
        y_pad = max(1.0, abs(y_min) * 0.1)
    else:
        y_pad = y_range * 0.1
    xs = _linspace(x_min, x_max, 300)

    plt.figure(figsize=(9, 6))
    plt.scatter(x_data, y_data, s=35, c="black", alpha=0.8, label="points du dataset")

    for i, arbre in enumerate(arbres):
        ys = _courbe_arbre(arbre, xs)
        label = labels[i] if i < len(labels) else f"fonction_{i + 1}"
        plt.plot(xs, ys, linewidth=2, label=label)

    # Axes fixes sur les donnees cibles pour garder des points visuellement stables.
    plt.xlim(x_min, x_max)
    plt.ylim(y_min - y_pad, y_max + y_pad)

    plt.title("Approximation symbolique : points vs fonctions")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.grid(alpha=0.25)
    plt.legend()

    if output_path is None:
        output_path = os.path.join(os.getcwd(), "evolution_plot.png")

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    plt.tight_layout()
    plt.savefig(output_path, dpi=140)
    plt.close()

    return output_path
