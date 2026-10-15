import pickle
import sys
from pathlib import Path

import folium
import networkx as nx
import osmnx as ox

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import (
    MAJOR_HIGHWAYS,
    MAP_CENTER,
    MAP_ZOOM,
    PROJECT_ROOT,
    SNAPPED_POINTS_PATH,
    ROUTE_PATH,
)
from data.graph_loader import load_main_graph, is_major_edge


# ---------- Базовые слои ----------

def base_map(location=MAP_CENTER, zoom=MAP_ZOOM, tiles="Esri.WorldGrayCanvas"):
    """Пустая карта с центром на НН."""
    return folium.Map(location=location, zoom_start=zoom, tiles=tiles)


def add_all_roads(m, G, color="#cccccc", weight=0.6, opacity=0.35):
    """Тонкий бледный слой со всеми дорогами (для контекста)."""
    edges_gdf = ox.graph_to_gdfs(G, nodes=False)
    edges_gdf.explore(
        m=m,
        color=color,
        weight=weight,
        opacity=opacity,
        legend=False,
    )
    return m


def add_major_roads(m, G, color="#1f77b4", weight=2, opacity=0.9):
    """Слой только с крупными дорогами."""
    keep = [
        (u, v, k) for u, v, k, d in G.edges(keys=True, data=True)
        if is_major_edge(d, MAJOR_HIGHWAYS)
    ]
    major = G.edge_subgraph(keep).copy()
    edges_gdf = ox.graph_to_gdfs(major, nodes=False)
    edges_gdf.explore(
        m=m,
        color=color,
        weight=weight,
        opacity=opacity,
        legend=False,
    )
    return m


def add_points(m, snapped, show_snapped=True):
    """Красные маркеры — исходные точки, синие кружки — привязанные узлы."""
    for i, (name, node, node_lat, node_lon) in enumerate(snapped):
        folium.Marker(
            location=[node_lat, node_lon],
            tooltip=f"{i}. {name}",
            icon=folium.Icon(color="red", icon="info-sign"),
        ).add_to(m)
        if show_snapped:
            folium.CircleMarker(
                location=[node_lat, node_lon],
                radius=3,
                color="blue",
                fill=True,
                fill_opacity=1.0,
                tooltip=f"{name} (узел графа)",
            ).add_to(m)
    return m


# ---------- Маршрут ----------

def build_full_path(G, nodes, route):
    """Склеивает кратчайшие пути между последовательными точками маршрута.

    nodes — список OSM-node-id, соответствующих точкам.
    route — порядок индексов (начинается и заканчивается стартовым индексом).
    Возвращает список OSM-node-id, по которым пройдёт курьер.
    """
    full = []
    for a, b in zip(route[:-1], route[1:]):
        seg = nx.shortest_path(G, nodes[a], nodes[b], weight="travel_time")
        if full:
            seg = seg[1:]
        full.extend(seg)
    return full


def add_route(m, G, full_path, total_sec=None):
    """Красная полилиния маршрута."""
    coords = [(G.nodes[n]["y"], G.nodes[n]["x"]) for n in full_path]
    tooltip = "Маршрут"
    if total_sec is not None:
        tooltip = f"Маршрут ({total_sec/60:.1f} мин)"
    folium.PolyLine(
        coords,
        color="#d62728",
        weight=4,
        opacity=0.9,
        tooltip=tooltip,
    ).add_to(m)
    return m


def add_route_markers(m, G, nodes, route, names):
    """Нумерованные маркеры в порядке посещения. Старт — зелёный."""
    for step, i in enumerate(route[:-1]):
        lat = G.nodes[nodes[i]]["y"]
        lon = G.nodes[nodes[i]]["x"]
        color = "green" if step == 0 else "red"
        icon = "flag" if step == 0 else "info-sign"
        folium.Marker(
            location=[lat, lon],
            tooltip=f"{step}. {names[i]}",
            popup=f"Шаг {step}: {names[i]}",
            icon=folium.Icon(color=color, icon=icon),
        ).add_to(m)
    return m


# ---------- Готовые сценарии ----------

def build_roads_map(G, out_path=None):
    """Только скелет крупных дорог."""
    m = base_map()
    add_major_roads(m, G)
    out_path = out_path or (PROJECT_ROOT / "map_roads.html")
    m.save(str(out_path))
    print(f"Готово: {out_path}")
    return m


def build_points_map(G, snapped, all_roads=False, out_path=None):
    """Скелет дорог + точки."""
    m = base_map()
    if all_roads:
        add_all_roads(m, G)
    add_major_roads(m, G)
    add_points(m, snapped)
    out_path = out_path or (PROJECT_ROOT / "map_points.html")
    m.save(str(out_path))
    print(f"Готово: {out_path}")
    return m


def build_route_map(G, snapped, route, total_sec, all_roads=True, out_path=None):
    """Скелет + (опционально все дороги) + точки + маршрут."""
    names = [s[0] for s in snapped]
    nodes = [s[1] for s in snapped]

    m = base_map()
    if all_roads:
        add_all_roads(m, G)
    add_major_roads(m, G)

    full_path = build_full_path(G, nodes, route)
    print(f"  Узлов в маршруте: {len(full_path)}")
    add_route(m, G, full_path, total_sec)
    add_route_markers(m, G, nodes, route, names)

    out_path = out_path or (PROJECT_ROOT / "map_route.html")
    m.save(str(out_path))
    print(f"Готово: {out_path}")
    return m


# ---------- CLI ----------

def _load_snapped():
    with open(SNAPPED_POINTS_PATH, "rb") as f:
        return pickle.load(f)


def _load_route():
    with open(ROUTE_PATH, "rb") as f:
        return pickle.load(f)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Генерация карт nn_courier")
    parser.add_argument(
        "mode",
        choices=["roads", "points", "route"],
        help="что рисовать",
    )
    parser.add_argument(
        "--all-roads",
        action="store_true",
        help="добавить слой со всеми дорогами (медленнее, но нагляднее)",
    )
    args = parser.parse_args()

    G = load_main_graph()

    if args.mode == "roads":
        build_roads_map(G)
    elif args.mode == "points":
        build_points_map(G, _load_snapped(), all_roads=args.all_roads)
    elif args.mode == "route":
        r = _load_route()
        build_route_map(
            G,
            _load_snapped(),
            r["route"],
            r["total_sec"],
            all_roads=args.all_roads,
        )