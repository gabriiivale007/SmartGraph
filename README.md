# SmartGraph

A lightweight, dependency-free Python library for **3D weighted directed graphs** with built-in pathfinding algorithms &mdash; designed for **maze generation, visualization, and solving**.

SmartGraph models mazes as graphs: cells are nodes on a grid, walls are the absence of edges, and corridors are weighted connections between adjacent cells. Multiple pathfinding algorithms find the way out.

---

## Features

- **Grid-based mazes** &mdash; cells identified by `(x, y, z)` coordinates with metadata (traps, bonuses, types)
- **Walls & corridors** &mdash; walls = no edge, corridors = bidirectional weighted edges
- **4 pathfinding algorithms** &mdash; Euclidean A\*, Dijkstra, A\* weighted, and longest-path DFS
- **Zero dependencies** &mdash; pure Python standard library, no pip installs required
- **Interactive GUI tools** &mdash; Tkinter-based maze viewer, solver, editor, and algorithm comparison
- **Memory efficient** &mdash; uses `__slots__` for optimized object storage
- **Fully type-hinted** &mdash; complete type annotations for IDE support

---

## Installation

Clone the repository and import directly:

```bash
git clone https://github.com/gabrielevalente/SmartGraph.git
```

```python
from smartgraph import Graph, Node, Edge
```

> **Requirements:** Python 3.9+ &mdash; Tkinter required only for GUI examples.

---

## Quick Start

```python
from smartgraph import Graph

# Create a maze
g = Graph()

# Add cells (nodes on a 2D grid, z=0)
g.add_node(0, 0, 0, {"nome": "Ingresso", "tipo": "ingresso"})
g.add_node(1, 0, 0, {"nome": "Corridoio"})
g.add_node(2, 0, 0, {"nome": "Corridoio"})
g.add_node(2, 1, 0, {"nome": "Uscita", "tipo": "uscita"})

# Open corridors between adjacent cells (bidirectional)
g.add_edge_bidi(0, 0, 0, 1, 0, 0, weight=1.0)
g.add_edge_bidi(1, 0, 0, 2, 0, 0, weight=1.0)
g.add_edge_bidi(2, 0, 0, 2, 1, 0, weight=1.0)
# No edge between (0,0) and (0,1) = wall!

# Solve the maze (Dijkstra)
result = g.shortest_path_weighted(0, 0, 0, 2, 1, 0)
if result:
    path, cost = result
    for cell in path:
        print(f"  -> ({cell.x:.0f},{cell.y:.0f})")
```

---

## Pathfinding Algorithms

| Algorithm | Method | Strategy | Best For |
|-----------|--------|----------|----------|
| **Euclidean A\*** | `shortest_path_euclidean()` | Minimizes physical distance | Shortest spatial path |
| **Dijkstra** | `shortest_path_weighted()` | Minimizes total edge weight | Safest/easiest route |
| **Weighted A\*** | `shortest_path_astar()` | Dijkstra + Euclidean heuristic | Faster weighted search |
| **Longest Path** | `longest_path_weighted()` | Maximizes total weight (DFS) | Explore the most rooms |

```python
# Shortest physical distance through the maze
path, distance = g.shortest_path_euclidean(0, 0, 0, 5, 3, 0)

# Safest route (lowest total difficulty)
path, cost = g.shortest_path_weighted(0, 0, 0, 5, 3, 0)

# Most adventurous path (highest total difficulty)
path, cost = g.longest_path_weighted(0, 0, 0, 5, 3, 0, max_visits=1)
```

All methods return `None` if no path exists (the maze has no solution).

---

## API Reference

### Graph

**Cell (node) management:**

| Method | Description |
|--------|-------------|
| `add_node(x, y, z, data=None)` | Add a cell at grid coordinates with optional metadata |
| `get_node(x, y, z)` | Retrieve a cell by coordinates |
| `remove_node(x, y, z)` | Remove a cell and all its corridors |
| `has_node(x, y, z)` | Check if a cell exists |
| `nodes` | List all cells |
| `node_count` | Total number of cells |

**Corridor (edge) management:**

| Method | Description |
|--------|-------------|
| `add_edge(x1, y1, z1, x2, y2, z2, weight=1.0)` | Open a one-way corridor |
| `add_edge_bidi(x1, y1, z1, x2, y2, z2, weight=1.0)` | Open a two-way corridor |
| `get_edges_from(x, y, z)` | Get all corridors leaving a cell |
| `get_neighbors(x, y, z)` | Get reachable cells from a cell |
| `remove_edge(x1, y1, z1, x2, y2, z2)` | Close a corridor (build a wall) |
| `has_edge(x1, y1, z1, x2, y2, z2)` | Check if a corridor exists |
| `edges` | List all corridors |
| `edge_count` | Total number of corridors |

**Cell data:**

| Method | Description |
|--------|-------------|
| `get_node_data(x, y, z)` | Get the full data dict of a cell |
| `set_node_data(x, y, z, data)` | Replace cell data entirely |
| `update_node_data(x, y, z, values)` | Merge values into cell data |
| `get_node_value(x, y, z, key, default)` | Read a single data field |
| `set_node_value(x, y, z, key, value)` | Write a single data field |

### Node

| Property/Method | Description |
|----------------|-------------|
| `x`, `y`, `z` | Cell coordinates |
| `coords` | Returns `(x, y, z)` tuple |
| `data` | Metadata dictionary |
| `distance_to(other)` | Euclidean distance to another cell |
| `get(key, default)` | Read from data dict |
| `set(key, value)` | Write to data dict |

### Edge

| Property | Description |
|----------|-------------|
| `source` | Source cell |
| `target` | Target cell |
| `weight` | Corridor weight/difficulty (non-negative float) |

---

## Examples

### Console Examples (`examples/`)

```bash
python examples/01_creazione_grafo.py      # Create a maze as a graph
python examples/02_gestione_dati_nodo.py   # Manage cell data (traps, items, state)
python examples/03_pathfinding_euclidea.py # Solve maze with Euclidean distance
python examples/04_pathfinding_dijkstra.py # Solve maze with Dijkstra & A*
python examples/05_pathfinding_costoso.py  # Find the longest path through the maze
python examples/06_scenario_completo.py    # Complete maze scenario: compare all algorithms
```

### GUI Examples (`esempi-tk/`)

Interactive Tkinter applications for visual maze exploration:

```bash
python esempi-tk/01_visualizza_grafo.py       # Maze visualization with hover & zoom
python esempi-tk/02_pathfinding_interattivo.py # Click-to-solve interactive maze
python esempi-tk/03_editor_grafo.py            # Build your own maze (click to add cells/corridors)
python esempi-tk/04_confronto_algoritmi.py     # Side-by-side algorithm comparison with animation
```

**GUI features:** color-coded cells (entrance, exit, traps, bonuses), wall rendering, hover tooltips, zoom, real-time path visualization, step-by-step animation.

---

## Project Structure

```
SmartGraph/
├── smartgraph/
│   ├── __init__.py          # Public API exports
│   ├── node.py              # Node class (grid cell)
│   ├── edge.py              # Edge class (corridor)
│   └── graph.py             # Graph class (maze structure + algorithms)
├── examples/                # 6 console-based maze examples
├── esempi-tk/               # 4 interactive Tkinter maze tools
│   └── theme.py             # Shared dark theme
├── LICENSE                  # MIT License
└── README.md
```

---

## How It Works

A maze is a graph where:

- **Cells** = nodes at integer grid coordinates `(x, y, 0)`
- **Walls** = absence of edges between adjacent cells
- **Corridors** = bidirectional weighted edges (`add_edge_bidi`)
- **Solving** = finding a path from entrance to exit using pathfinding algorithms

```
  Cell ---- Corridor ---- Cell          Cell
   |                                     |
Corridor                              Corridor
   |                                     |
  Cell      WALL         Cell ---- ---- Cell
```

---

## License

MIT License &copy; 2026 Gabriele Valente &mdash; see [LICENSE](LICENSE) for details.
