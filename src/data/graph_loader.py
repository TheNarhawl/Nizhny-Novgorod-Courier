import pickle
import sys
from pathlib import Path

import osmnx as ox
import networkx as nx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import NN_BBOX, NETWORK_TYPE, GRAPH_PATH, GRAPH_MAIN_PATH


def download_graph(bbox=NN_BBOX, network_type=NETWORK_TYPE) -> nx.MultiDiGraph:
    """Скачивает граф дорог по bbox и добавляет скорости/времена."""
    print(f"Скачиваем граф по bbox={bbox}, network_type={network_type}...")
    G = ox.graph_from_bbox(bbox, network_type=network_type)
    print(f"  Узлов: {G.number_of_nodes()}, рёбер: {G.number_of_edges()}")
    G = ox.add_edge_speeds(G)
    G = ox.add_edge_travel_times(G)
    return G


def save_graph(G: nx.MultiDiGraph, path=GRAPH_PATH) -> None:
    with open(path, "wb") as f:
        pickle.dump(G, f)
    print(f"Сохранили {path}")


def load_graph(path=GRAPH_PATH) -> nx.MultiDiGraph:
    with open(path, "rb") as f:
        return pickle.load(f)


def get_main_component(G: nx.MultiDiGraph) -> nx.MultiDiGraph:
    """Возвращает подграф на крупнейшей слабо связной компоненте."""
    comps = sorted(nx.weakly_connected_components(G), key=len, reverse=True)
    print(f"  Компонент: {len(comps)}, крупнейшая: {len(comps[0])} "
          f"({100*len(comps[0])/G.number_of_nodes():.1f}%)")
    return G.subgraph(comps[0]).copy()


def is_major_edge(data: dict, major_set: set) -> bool:
    """Проверяет, относится ли ребро к крупной дороге."""
    hw = data.get("highway")
    if isinstance(hw, list):
        return any(h in major_set for h in hw)
    return hw in major_set


def load_main_graph(path=GRAPH_MAIN_PATH) -> nx.MultiDiGraph:
    """Удобный shortcut для остальных модулей."""
    return load_graph(path)


if __name__ == "__main__":
    if GRAPH_PATH.exists():
        print(f"{GRAPH_PATH} уже существует — пропускаем скачивание.")
        G = load_graph()
    else:
        G = download_graph()
        save_graph(G)

    if GRAPH_MAIN_PATH.exists():
        print(f"{GRAPH_MAIN_PATH} уже существует — пропускаем.")
    else:
        G_main = get_main_component(G)
        save_graph(G_main, GRAPH_MAIN_PATH)

    print("Готово.")