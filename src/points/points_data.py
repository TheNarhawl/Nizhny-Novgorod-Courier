import pickle
import sys
from pathlib import Path

import osmnx as ox

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import SNAPPED_POINTS_PATH

POINTS = [
    ("Та самая шаурма на Средном", 56.327541, 44.007847),
    ("Галерея Юрковка", 56.323048, 43.991238),
]

def snap_to_graph(G, points=POINTS):
    """Привязывает точки к ближайшим узлам графа.

    Возвращает список кортежей (name, node, node_lat, node_lon).
    """
    snapped = []
    for name, lat, lon in points:
        node = ox.distance.nearest_nodes(G, X=lon, Y=lat)
        node_lat = G.nodes[node]["y"]
        node_lon = G.nodes[node]["x"]
        dx = ox.distance.great_circle(lat, lon, node_lat, node_lon)
        print(f"  {name:25s} -> узел {node} (сдвиг {dx:.0f} м)")
        snapped.append((name, node, node_lat, node_lon))
    return snapped


def save_snapped(snapped, path=SNAPPED_POINTS_PATH):
    with open(path, "wb") as f:
        pickle.dump(snapped, f)
    print(f"Сохранили {path}")


def load_snapped(path=SNAPPED_POINTS_PATH):
    with open(path, "rb") as f:
        return pickle.load(f)


if __name__ == "__main__":
    from data.graph_loader import load_main_graph

    G = load_main_graph()
    snapped = snap_to_graph(G, POINTS)
    save_snapped(snapped)