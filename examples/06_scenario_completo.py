"""Esempio 06 — Scenario completo: confronto algoritmi su un labirinto."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from smartgraph import Graph

g = Graph()

celle = {
    "Ingresso":    (0, 0),
    "Sala_Armi":   (1, 0),
    "Biblioteca":  (2, 0),
    "Pozzo":       (4, 0),
    "Torretta":    (5, 0),
    "Prigione":    (0, 1),
    "Laboratorio": (2, 1),
    "Cripta":      (3, 1),
    "Armeria":     (4, 1),
    "Cantine":     (0, 2),
    "Cucina":      (1, 2),
    "Cappella":    (2, 2),
    "Galleria":    (3, 2),
    "Tesoro":      (4, 2),
    "Giardino":    (0, 3),
    "Cortile":     (1, 3),
    "Fontana":     (2, 3),
    "Ponte":       (3, 3),
    "Uscita":      (4, 3),
}

for nome, (x, y) in celle.items():
    g.add_node(x, y, 0, {"nome": nome, "tipo": "cella"})

g.update_node_data(0, 0, 0, {"tipo": "ingresso"})
g.update_node_data(4, 3, 0, {"tipo": "uscita"})
g.update_node_data(4, 0, 0, {"trappola": "caduta"})
g.update_node_data(3, 1, 0, {"trappola": "scheletri"})
g.update_node_data(4, 2, 0, {"bonus": "chiave d'oro"})
g.update_node_data(1, 0, 0, {"bonus": "spada"})

corridoi = [
    ("Ingresso",    "Sala_Armi",    2),
    ("Sala_Armi",   "Biblioteca",   1),
    ("Ingresso",    "Prigione",     3),
    ("Pozzo",       "Torretta",     4),
    ("Biblioteca",  "Cripta",       6),
    ("Prigione",    "Cantine",      2),
    ("Laboratorio", "Cripta",       3),
    ("Cripta",      "Armeria",      5),
    ("Torretta",    "Armeria",      7),
    ("Cantine",     "Cucina",       1),
    ("Cucina",      "Cortile",      2),
    ("Cappella",    "Galleria",     1),
    ("Galleria",    "Tesoro",       3),
    ("Laboratorio", "Cappella",     2),
    ("Tesoro",      "Uscita",       4),
    ("Giardino",    "Cortile",      1),
    ("Cortile",     "Fontana",      2),
    ("Fontana",     "Ponte",        1),
    ("Ponte",       "Uscita",       2),
    ("Armeria",     "Tesoro",       8),
    ("Pozzo",       "Armeria",      3),
]

for src_name, dst_name, cost in corridoi:
    src = celle[src_name]
    dst = celle[dst_name]
    g.add_edge_bidi(*src, 0, *dst, 0, weight=cost)

print(f"Labirinto: {g}")
print(f"{'='*60}")

src = celle["Ingresso"]
dst = celle["Uscita"]

res_near = g.shortest_path_euclidean(*src, 0, *dst, 0)
if res_near:
    path, dist = res_near
    nomi = [g.get_node_value(*n.coords, "nome") for n in path]
    print(f"\n1. VICINO (distanza euclidea):")
    print(f"   {' -> '.join(nomi)}")
    print(f"   Distanza totale: {dist:.2f} celle")
    print(f"   Stanze attraversate: {len(path)}")

res_cheap = g.shortest_path_weighted(*src, 0, *dst, 0)
if res_cheap:
    path, cost = res_cheap
    nomi = [g.get_node_value(*n.coords, "nome") for n in path]
    print(f"\n2. SICURO (costo minimo — Dijkstra):")
    print(f"   {' -> '.join(nomi)}")
    print(f"   Difficolta' totale: {cost}")
    print(f"   Stanze attraversate: {len(path)}")

res_expensive = g.longest_path_weighted(*src, 0, *dst, 0)
if res_expensive:
    path, cost = res_expensive
    nomi = [g.get_node_value(*n.coords, "nome") for n in path]
    print(f"\n3. AVVENTUROSO (costo massimo):")
    print(f"   {' -> '.join(nomi)}")
    print(f"   Difficolta' totale: {cost}")
    print(f"   Stanze attraversate: {len(path)}")

print(f"\n{'='*60}")
print("Riepilogo comparativo:")
if res_near:
    print(f"  Piu' vicino:      distanza = {res_near[1]:.2f}, stanze = {len(res_near[0])}")
if res_cheap:
    print(f"  Piu' sicuro:      costo = {res_cheap[1]}, stanze = {len(res_cheap[0])}")
if res_expensive:
    print(f"  Piu' avventuroso: costo = {res_expensive[1]}, stanze = {len(res_expensive[0])}")
