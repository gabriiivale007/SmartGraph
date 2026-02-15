"""Esempio 02 — Gestione dei dati delle celle del labirinto."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from smartgraph import Graph

g = Graph()

g.add_node(0, 0, 0, {
    "nome": "Stanza del Tesoro",
    "tipo": "stanza",
    "visitata": False,
    "oggetti": ["chiave d'oro", "mappa"],
    "pericolo": 0,
})

# Lettura
print("=== Lettura dati della cella ===")
data = g.get_node_data(0, 0, 0)
print(f"Payload completo: {data}")

tipo = g.get_node_value(0, 0, 0, "tipo")
print(f"Tipo cella: {tipo}")

trappola = g.get_node_value(0, 0, 0, "trappola", default="nessuna")
print(f"Trappola: {trappola}")

# Il giocatore visita la stanza
print("\n=== Il giocatore entra nella stanza ===")
g.set_node_value(0, 0, 0, "visitata", True)
g.set_node_value(0, 0, 0, "pericolo", 3)
print(f"Dopo visita: {g.get_node_data(0, 0, 0)}")

# Merge: raccoglie la chiave
print("\n=== Il giocatore raccoglie la chiave ===")
g.update_node_data(0, 0, 0, {
    "oggetti": ["mappa"],
    "ultimo_visitatore": "Giocatore 1",
    "turno_visita": 5,
})
print(f"Dopo raccolta: {g.get_node_data(0, 0, 0)}")

# Sovrascrittura completa
print("\n=== Reset della stanza ===")
g.set_node_data(0, 0, 0, {"nome": "Stanza del Tesoro", "tipo": "stanza", "visitata": False})
print(f"Dopo reset: {g.get_node_data(0, 0, 0)}")

# Accesso diretto al Node
print("\n=== Accesso diretto al Node ===")
node = g.get_node(0, 0, 0)
node.set("trappola", "frecce avvelenate")
print(f"Via Node.set: {node.data}")
print(f"Via Node.get: trappola = {node.get('trappola')}")
