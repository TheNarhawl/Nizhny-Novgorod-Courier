import pickle
import sys
from pathlib import Path

import networkx as nx
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import MATRIX_PATH, MATRIX_META_PATH
from data.graph_loader import load_main_graph


def build_matrix(G: nx.MultiDiGraph, nodes: list, names: list) -> np.ndarray:
    """Считает матрицу времён (сек) между всеми парами узлов.

    nodes — список OSM-node-id, names — подписи для логов.
    """
    n = len(nodes)
    D = np.full((n, n), np.inf, dtype=float)

    for i, src in enumerate(nodes):
        lengths = nx.single_source_dijkstra_path_length(
            G, src, weight="travel_time"
        )
        for j, dst in enumerate(nodes):
            if dst in lengths:
                D[i, j] = lengths[dst]
        print(f"  {names[i]:25s} -> {len(lengths)} достижимых узлов")

    n_inf = int(np.isinf(D).sum())
    print(f"  inf-значений: {n_inf} из {n*n}")
    if n_inf:
        print("  ВНИМАНИЕ: часть точек недостижима — граф, возможно, не связный.")
    return D


def save_matrix(D: np.ndarray, names: list, nodes: list) -> None:
    np.save(MATRIX_PATH, D)
    with open(MATRIX_META_PATH, "wb") as f:
        pickle.dump({"names": names, "nodes": nodes}, f)
    print(f"Сохранили {MATRIX_PATH} и {MATRIX_META_PATH}")


def load_matrix():
    D = np.load(MATRIX_PATH)
    with open(MATRIX_META_PATH, "rb") as f:
        meta = pickle.load(f)
    return D, meta["names"], meta["nodes"]


if __name__ == "__main__":
    from config import SNAPPED_POINTS_PATH

    with open(SNAPPED_POINTS_PATH, "rb") as f:
        snapped = pickle.load(f)

    names = [s[0] for s in snapped]
    nodes = [s[1] for s in snapped]

    G = load_main_graph()
    D = build_matrix(G, nodes, names)
    save_matrix(D, names, nodes)