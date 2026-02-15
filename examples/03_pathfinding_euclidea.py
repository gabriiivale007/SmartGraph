"""Esempio 03 — Risoluzione labirinto con distanza euclidea."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from smartgraph import Graph

g = Graph()

# Labirinto 5x5
#
#   S --- . --- .     .     .
#   |           |           |
#   .     . --- .     . --- .
#         |           |
#   . --- . --- . --- .     .
#   |                       |
#   .     . --- .     . --- E
#   |     |           |
#   . --- .     . --- .

nomi = {
    (0, 0): "Start", (1, 0): "A1", (2, 0): "A2", (3, 0): "A3", (4, 0): "A4",
    (0, 1): "B0", (1, 1): "B1", (2, 1): "B2", (3, 1): "B3", (4, 1): "B4",
    (0, 2): "C0", (1, 2): "C1", (2, 2): "C2", (3, 2): "C3", (4, 2): "C4",
    (0, 3): "D0", (1, 3): "D1", (2, 3): "D2", (3, 3): "D3", (4, 3): "Uscita",
    (0, 4): "E0", (1, 4): "E1", (2, 4): "E2", (3, 4): "E3",
}
for (x, y), nome in nomi.items():
    g.add_node(x, y, 0, {"nome": nome})

corridoi = [
    (0,0, 1,0), (1,0, 2,0),
    (1,1, 2,1), (3,1, 4,1),
    (0,2, 1,2), (1,2, 2,2), (2,2, 3,2),
    (1,3, 2,3), (3,3, 4,3),
    (0,4, 1,4), (2,4, 3,4),
    (0,0, 0,1), (0,2, 0,3), (0,3, 0,4),
    (1,1, 1,2), (1,3, 1,4),
    (2,0, 2,1),
    (3,1, 3,2), (3,3, 3,4),
    (4,0, 4,1), (4,2, 4,3),
]
for x1, y1, x2, y2 in corridoi:
    g.add_edge_bidi(x1, y1, 0, x2, y2, 0, weight=1.0)


def stampa_percorso(label, result):
    if result is None:
        print(f"\n{label}: Nessun percorso trovato!")
        return
    path, dist = result
    nomi_path = [g.get_node_value(*n.coords, "nome") for n in path]
    print(f"\n{label}:")
    print(f"  Percorso:  {' -> '.join(nomi_path)}")
    print(f"  Celle attraversate: {len(path)}")
    print(f"  Distanza euclidea totale: {dist:.4f}")


result = g.shortest_path_euclidean(0, 0, 0, 4, 3, 0)
stampa_percorso("Percorso piu' BREVE (distanza euclidea)", result)

start = g.get_node(0, 0, 0)
uscita = g.get_node(4, 3, 0)
print(f"\n  Distanza in linea d'aria Start->Uscita: {start.distance_to(uscita):.4f}")
