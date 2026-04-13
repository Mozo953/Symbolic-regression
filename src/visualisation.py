import math
import os


def _linspace(x_min, x_max, n):
    if n <= 1:
        return [x_min]
    step = (x_max - x_min) / (n - 1)
    return [x_min + i * step for i in range(n)]


def _tree_curve(tree, xs):
    ys = []
    for x in xs:
        try:
            y = tree.evaluate(x)
            if y is None or not math.isfinite(float(y)):
                ys.append(float("nan"))
            else:
                ys.append(float(y))
        except Exception:
            ys.append(float("nan"))
    return ys


def plot_points_and_functions(data, trees, labels=None, output_path=None):
    """Plot target points plus one or more tree functions on the same graph."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as exc:
        print("Unable to plot (matplotlib unavailable):", exc)
        return None

    if not data:
        print("No data to plot.")
        return None

    if labels is None:
        labels = [f"function_{i + 1}" for i in range(len(trees))]

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
    plt.scatter(x_data, y_data, s=35, c="black", alpha=0.8, label="dataset points")

    for i, tree in enumerate(trees):
        ys = _tree_curve(tree, xs)
        label = labels[i] if i < len(labels) else f"function_{i + 1}"
        plt.plot(xs, ys, linewidth=2, label=label)

    # Keep axes fixed on target data so points remain visually stable.
    plt.xlim(x_min, x_max)
    plt.ylim(y_min - y_pad, y_max + y_pad)

    plt.title("Symbolic approximation: points vs functions")
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
