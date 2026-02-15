"""Esempio 05 — Percorso piu' lungo nel labirinto (DFS con cicli)."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from smartgraph import Graph

g = Graph()

# Labirinto con ciclo
#
#   S --5-- A --3-- B
#   |       ^       |
#   1       3       2
#   |       |       |
#   C --7-- D <--+  U
#                |
#                +--- (B -> D, D -> A)

celle = {
    "Start": (0, 0), "A": (1, 0), "B": (2, 0),
    "C": (0, 1), "D": (1, 1), "Uscita": (2, 1),
}

for nome, (x, y) in celle.items():
    g.add_node(x, y, 0, {"nome": nome})

g.add_edge_bidi(0, 0, 0,  1, 0, 0, weight=5)
g.add_edge_bidi(0, 0, 0,  0, 1, 0, weight=1)
g.add_edge_bidi(1, 0, 0,  2, 0, 0, weight=3)
g.add_edge_bidi(0, 1, 0,  1, 1, 0, weight=7)
g.add_edge(1, 1, 0,  1, 0, 0, weight=3)         # D -> A
g.add_edge(2, 0, 0,  2, 1, 0, weight=2)         # B -> U
g.add_edge(2, 0, 0,  1, 1, 0, weight=2)         # B -> D (ciclo)


def stampa(label, result):
    if result is None:
        print(f"\n{label}: Nessun percorso trovato!")
        return
    path, cost = result
    nomi_path = [g.get_node_value(*n.coords, "nome") for n in path]
    print(f"\n{label}:")
    print(f"  Percorso: {' -> '.join(nomi_path)}")
    print(f"  Punti raccolti: {cost}")
    print(f"  Celle attraversate: {len(path)}")


result = g.longest_path_weighted(0, 0, 0, 2, 1, 0, max_visits=1)
stampa("Percorso piu' LUNGO (senza rivisitare celle)", result)

result2 = g.longest_path_weighted(0, 0, 0, 2, 1, 0, max_visits=2)
stampa("Percorso piu' LUNGO (max 2 visite per cella)", result2)

result_cheap = g.shortest_path_weighted(0, 0, 0, 2, 1, 0)
stampa("Percorso piu' BREVE (riferimento)", result_cheap)

if result and result_cheap:
    print(f"\n  Differenza di punti: {result[1] - result_cheap[1]}")
