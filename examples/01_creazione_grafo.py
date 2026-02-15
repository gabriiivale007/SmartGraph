"""Esempio 01 — Creazione di un labirinto come grafo."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from smartgraph import Graph

# Labirinto 4x3:
#
#   (0,0) --- (1,0) --- (2,0) --- (3,0)
#     |                   |         |
#   (0,1)     (1,1) --- (2,1)     (3,1)
#     |         |                   |
#   (0,2) --- (1,2) --- (2,2) --- (3,2)

g = Graph()

celle = [
    (0, 0, 0, {"nome": "Ingresso",  "tipo": "ingresso"}),
    (1, 0, 0, {"nome": "Corridoio", "tipo": "corridoio"}),
    (2, 0, 0, {"nome": "Corridoio", "tipo": "corridoio"}),
    (3, 0, 0, {"nome": "Corridoio", "tipo": "corridoio"}),
    (0, 1, 0, {"nome": "Corridoio", "tipo": "corridoio"}),
    (1, 1, 0, {"nome": "Corridoio", "tipo": "corridoio"}),
    (2, 1, 0, {"nome": "Corridoio", "tipo": "corridoio"}),
    (3, 1, 0, {"nome": "Corridoio", "tipo": "corridoio"}),
    (0, 2, 0, {"nome": "Corridoio", "tipo": "corridoio"}),
    (1, 2, 0, {"nome": "Corridoio", "tipo": "corridoio"}),
    (2, 2, 0, {"nome": "Corridoio", "tipo": "corridoio"}),
    (3, 2, 0, {"nome": "Uscita",    "tipo": "uscita"}),
]

for x, y, z, data in celle:
    g.add_node(x, y, z, data)

# Corridoi — dove non c'e' arco c'e' un muro
g.add_edge_bidi(0, 0, 0,  1, 0, 0, weight=1.0)
g.add_edge_bidi(1, 0, 0,  2, 0, 0, weight=1.0)
g.add_edge_bidi(2, 0, 0,  3, 0, 0, weight=1.0)

g.add_edge_bidi(0, 0, 0,  0, 1, 0, weight=1.0)
g.add_edge_bidi(2, 0, 0,  2, 1, 0, weight=1.0)
g.add_edge_bidi(3, 0, 0,  3, 1, 0, weight=1.0)

g.add_edge_bidi(1, 1, 0,  2, 1, 0, weight=1.0)

g.add_edge_bidi(0, 1, 0,  0, 2, 0, weight=1.0)
g.add_edge_bidi(1, 1, 0,  1, 2, 0, weight=1.0)
g.add_edge_bidi(3, 1, 0,  3, 2, 0, weight=1.0)

g.add_edge_bidi(0, 2, 0,  1, 2, 0, weight=1.0)
g.add_edge_bidi(1, 2, 0,  2, 2, 0, weight=1.0)
g.add_edge_bidi(2, 2, 0,  3, 2, 0, weight=1.0)

print(f"Labirinto creato: {g}")
print(f"  Celle: {g.node_count}")
print(f"  Corridoi (archi): {g.edge_count}")

print("\nLista celle:")
for node in g.nodes:
    print(f"  ({node.x:.0f},{node.y:.0f}) {node.data}")

print("\nVicini raggiungibili da (0,0) [Ingresso]:")
for n in g.get_neighbors(0, 0, 0):
    print(f"  -> ({n.x:.0f},{n.y:.0f}) {n.get('nome')}")

print("\nVicini raggiungibili da (1,1):")
for n in g.get_neighbors(1, 1, 0):
    print(f"  -> ({n.x:.0f},{n.y:.0f}) {n.get('nome')}")
