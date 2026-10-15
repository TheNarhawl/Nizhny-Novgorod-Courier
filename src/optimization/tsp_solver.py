import pickle
import sys
from pathlib import Path

import numpy as np
from ortools.constraint_solver import routing_enums_pb2, pywrapcp

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import MATRIX_PATH, MATRIX_META_PATH, ROUTE_PATH


def solve_tsp(D: np.ndarray, time_limit_sec: int = 5, start: int = 0):
    """Решает замкнутый TSP. D[i][j] — время в секундах.

    Возвращает (route, total_sec):
      route — список индексов точек в порядке обхода, начиная и заканчивая start.
      total_sec — общее время в пути.
    """
    n = D.shape[0]

    D_int = np.where(np.isinf(D), 10**9, D).astype(int) * 1000

    manager = pywrapcp.RoutingIndexManager(n, 1, start)
    routing = pywrapcp.RoutingModel(manager)

    def time_cb(from_idx, to_idx):
        i = manager.IndexToNode(from_idx)
        j = manager.IndexToNode(to_idx)
        return int(D_int[i, j])

    routing.SetArcCostEvaluatorOfAllVehicles(routing.RegisterTransitCallback(time_cb))

    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    params.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    params.time_limit.FromSeconds(time_limit_sec)

    solution = routing.SolveWithParameters(params)
    if not solution:
        raise RuntimeError("TSP: решение не найдено")

    route = []
    total_ms = 0
    idx = routing.Start(0)
    while not routing.IsEnd(idx):
        route.append(manager.IndexToNode(idx))
        nxt = solution.Value(routing.NextVar(idx))
        total_ms += routing.GetArcCostForVehicle(idx, nxt, 0)
        idx = nxt
    route.append(manager.IndexToNode(idx))

    return route, total_ms / 1000


def save_route(route, total_sec, names):
    with open(ROUTE_PATH, "wb") as f:
        pickle.dump({"route": route, "total_sec": total_sec, "names": names}, f)
    print(f"Сохранили {ROUTE_PATH}")


def load_route():
    with open(ROUTE_PATH, "rb") as f:
        return pickle.load(f)


if __name__ == "__main__":
    D = np.load(MATRIX_PATH)
    with open(MATRIX_META_PATH, "rb") as f:
        meta = pickle.load(f)
    names = meta["names"]

    print("Решаем TSP...")
    route, total_sec = solve_tsp(D, time_limit_sec=5, start=0)

    print("\nПорядок посещения:")
    for step, i in enumerate(route):
        marker = ""
        if step == 0:
            marker = " (старт)"
        elif step == len(route) - 1:
            marker = " (финиш = старт)"
        print(f"  {step}. {names[i]:25s}{marker}")

    print(f"\nОбщее время: {total_sec/60:.1f} мин")
    save_route(route, total_sec, names)