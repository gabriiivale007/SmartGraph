"""Esempio 04 — Risoluzione labirinto con Dijkstra & A*."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from smartgraph import Graph

g = Graph()

# Labirinto con costi variabili
#
#   S --1-- A --5-- B --1-- C
#   |                       |
#   3               2       1
#   |               |       |
#   D --2-- E --1-- F       G
#           |               |
#           4       1       3
#           |       |       |
#   H --1-- I --1-- J --1-- U

celle = {
    "Start": (0, 0), "A": (1, 0), "B": (2, 0), "C": (3, 0),
    "D": (0, 1), "E": (1, 1), "F": (2, 1), "G": (3, 1),
    "H": (0, 2), "I": (1, 2), "J": (2, 2), "Uscita": (3, 2),
}

for nome, (x, y) in celle.items():
    g.add_node(x, y, 0, {"nome": nome})

corridoi = [
    ("Start", "A", 1), ("A", "B", 5), ("B", "C", 1),
    ("Start", "D", 3),
    ("C", "G", 1),
    ("D", "E", 2), ("E", "F", 1),
    ("E", "I", 4), ("F", "J", 1), ("G", "Uscita", 3),
    ("H", "I", 1), ("I", "J", 1), ("J", "Uscita", 1),
]

for src_name, dst_name, costo in corridoi:
    src = celle[src_name]
    dst = celle[dst_name]
    g.add_edge_bidi(*src, 0, *dst, 0, weight=costo)


def stampa(label, result):
    if result is None:
        print(f"\n{label}: Nessun percorso trovato!")
        return
    path, cost = result
    nomi_path = [g.get_node_value(*n.coords, "nome") for n in path]
    print(f"\n{label}:")
    print(f"  Percorso: {' -> '.join(nomi_path)}")
    print(f"  Costo totale: {cost}")
    print(f"  Celle attraversate: {len(path)}")


result_dj = g.shortest_path_weighted(0, 0, 0, 3, 2, 0)
stampa("Dijkstra — percorso meno pericoloso", result_dj)

result_astar = g.shortest_path_astar(0, 0, 0, 3, 2, 0)
stampa("A* — percorso meno pericoloso", result_astar)

if result_dj and result_astar:
    assert result_dj[1] == result_astar[1], "I costi devono essere uguali!"
    print("\n  Dijkstra e A* concordano sul costo ottimale.")
