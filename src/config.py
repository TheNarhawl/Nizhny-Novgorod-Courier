from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

GRAPH_PATH = DATA_DIR / "graph_nn.pkl"
GRAPH_MAIN_PATH = DATA_DIR / "graph_nn_main.pkl"
MATRIX_PATH = DATA_DIR / "matrix.npy"
MATRIX_META_PATH = DATA_DIR / "matrix_meta.pkl"
SNAPPED_POINTS_PATH = DATA_DIR / "snapped_points.pkl"
ROUTE_PATH = DATA_DIR / "route.pkl"

NN_BBOX = (43.65, 56.15, 44.20, 56.45)
NETWORK_TYPE = "drive"

MAP_CENTER = (56.326, 44.005)
MAP_ZOOM = 12

MAJOR_HIGHWAYS = {
    "motorway", "motorway_link",
    "trunk", "trunk_link",
    "primary", "primary_link",
    "secondary", "secondary_link",
    "tertiary", "tertiary_link",
}