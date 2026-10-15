# Nizhny Novgorod Courier

<img width="1917" height="917" alt="image" src="https://github.com/user-attachments/assets/f261558b-30e6-49f4-a8f3-7eddd8eb9c32" />

Оптимизатор маршрута курьера по дорогам Нижнего Новгорода.

По списку адресов строит наиболее быстрый порядок объезда (задача коммивояжёра,
TSP) с учётом реальной дорожной сети OSM и визуализирует маршрут на
интерактивной карте.

## Что делает

1. Скачивает граф дорог Нижнего Новгорода из OpenStreetMap.
2. Привязывает точки курьера к ближайшим узлам графа.
3. Считает матрицу времён проезда между всеми парами точек.
4. Решает TSP (замкнутый маршрут) через OR-Tools.
5. Строит HTML-карту с дорогами, точками и маршрутом.

## Стек

- [OSMnx](https://osmnx.readthedocs.io/) — загрузка графа дорог из OSM
- [NetworkX](https://networkx.org/) — кратчайшие пути
- [OR-Tools](https://developers.google.com/optimization) — TSP/VRP решение
- [Folium](https://python-visualization.github.io/folium/) — интерактивные карты
- [uv](https://docs.astral.sh/uv/) — управление зависимостями

## Структура проекта

```
nn_courier/
├── src/
│   ├── config.py                  # настройки и пути
│   ├── data/
│   │   ├── graph_loader.py        # загрузка графа OSM
│   │   └── matrix_builder.py      # матрица времён между точками
│   ├── points/
│   │   └── points_data.py         # список точек + привязка к графу
│   ├── optimization/
│   │   └── tsp_solver.py          # TSP через OR-Tools
│   └── visualization/
│       └── map_builder.py         # HTML-карты
├── data/                          # сгенерированные артефакты (gitignored)
├── tests/
├── pyproject.toml
├── uv.lock
└── README.md
```

## Установка

Python 3.10+.

### Через uv (рекомендуется)

```bash
git clone <repo-url>
cd nn_courier
uv sync
```

### Через pip

```bash
python -m venv .venv
.venv\Scripts\activate     # Windows
source .venv/bin/activate  # Linux / macOS
pip install osmnx networkx matplotlib folium mapclassify ortools numpy
```

## Использование

### 1. Скачать граф дорог

```bash
python src/data/graph_loader.py
```

Загружает граф по bbox Нижнего Новгорода (`config.NN_BBOX`) и сохраняет в
`data/graph_nn.pkl` и `data/graph_nn_main.pkl`. Первый запуск — 30–90 сек,
дальше скрипт пропускает скачивание, если файлы уже есть.

### 2. Задать точки курьера

Отредактируй список `POINTS` в `src/points/points_data.py`:

```python
POINTS = [
    ("Кремль",              56.3287, 44.0020),
    ("Московский вокзал",   56.3217, 43.9457),
    # ...
]
```

Формат: `(название, широта, долгота)`.

Затем привязать точки к графу:

```bash
python src/points/points_data.py
```

### 3. Построить матрицу времён

```bash
python src/data/matrix_builder.py
```

### 4. Решить TSP

```bash
python src/optimization/tsp_solver.py
```

Выведет порядок посещения и общее время в пути.

### 5. Сгенерировать карту маршрута

```bash
python src/visualization/map_builder.py route
```

Открой `map_route.html` в браузере — увидишь дороги, точки и маршрут.

Доступные режимы:

```bash
python src/visualization/map_builder.py roads            # только дороги
python src/visualization/map_builder.py points           # дороги + точки
python src/visualization/map_builder.py route --all-roads  # маршрут + все дороги
```

## Полный цикл одной командой

```bash
python src/points/points_data.py && \
python src/data/matrix_builder.py && \
python src/optimization/tsp_solver.py && \
python src/visualization/map_builder.py route
```

Если меняешь список точек — всегда прогоняй все шаги заново: артефакты в
`data/` связаны между собой, и `route.pkl` перестанет соответствовать
`snapped_points.pkl`, если обновить только часть.

## Настройки

Всё лежит в `src/config.py`:

- `NN_BBOX` — область загрузки графа
- `NETWORK_TYPE` — `drive`, `walk`, `bike`
- `MAP_CENTER`, `MAP_ZOOM` — центр и зум карт
- `MAJOR_HIGHWAYS` — какие дороги рисовать жирно
