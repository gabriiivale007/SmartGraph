from __future__ import annotations

import heapq
from typing import Any

from smartgraph.edge import Edge
from smartgraph.node import Node


class Graph:

    def __init__(self) -> None:
        self._nodes: dict[tuple[float, float, float], Node] = {}
        self._adj: dict[tuple[float, float, float], list[Edge]] = {}

    # ------------------------------------------------------------------
    #  Proprieta'
    # ------------------------------------------------------------------

    @property
    def nodes(self) -> list[Node]:
        """Restituisce tutti i nodi del grafo."""
        return list(self._nodes.values())

    @property
    def edges(self) -> list[Edge]:
        """Restituisce tutti gli archi del grafo."""
        result: list[Edge] = []
        for edge_list in self._adj.values():
            result.extend(edge_list)
        return result

    @property
    def node_count(self) -> int:
        return len(self._nodes)

    @property
    def edge_count(self) -> int:
        return sum(len(el) for el in self._adj.values())

    # ------------------------------------------------------------------
    #  Gestione nodi
    # ------------------------------------------------------------------

    def add_node(
        self, x: float, y: float, z: float, data: dict[str, Any] | None = None
    ) -> Node:
        """Aggiunge un nodo al grafo. Se esiste gia', restituisce quello esistente."""
        key = (float(x), float(y), float(z))
        if key in self._nodes:
            return self._nodes[key]
        node = Node(x, y, z, data)
        self._nodes[key] = node
        self._adj[key] = []
        return node

    def get_node(self, x: float, y: float, z: float) -> Node | None:
        """Restituisce il nodo alle coordinate date, o None."""
        return self._nodes.get((float(x), float(y), float(z)))

    def remove_node(self, x: float, y: float, z: float) -> bool:
        """Rimuove un nodo e tutti gli archi collegati. Restituisce True se rimosso."""
        key = (float(x), float(y), float(z))
        if key not in self._nodes:
            return False
        del self._nodes[key]
        del self._adj[key]
        for src_key in list(self._adj):
            self._adj[src_key] = [e for e in self._adj[src_key] if e.target.coords != key]
        return True

    def has_node(self, x: float, y: float, z: float) -> bool:
        return (float(x), float(y), float(z)) in self._nodes

    # ------------------------------------------------------------------
    #  Gestione dati dei nodi
    # ------------------------------------------------------------------

    def get_node_data(self, x: float, y: float, z: float) -> dict[str, Any] | None:
        """Restituisce il payload del nodo, o None se non esiste."""
        node = self.get_node(x, y, z)
        return node.data if node else None

    def set_node_data(
        self, x: float, y: float, z: float, data: dict[str, Any]
    ) -> bool:
        """Sostituisce interamente il payload del nodo. Restituisce True se trovato."""
        node = self.get_node(x, y, z)
        if node is None:
            return False
        node.data = dict(data)
        return True

    def update_node_data(
        self, x: float, y: float, z: float, values: dict[str, Any]
    ) -> bool:
        """Aggiorna (merge) il payload del nodo. Restituisce True se trovato."""
        node = self.get_node(x, y, z)
        if node is None:
            return False
        node.update(values)
        return True

    def get_node_value(self, x: float, y: float, z: float, key: str, default: Any = None) -> Any:
        """Legge un singolo campo dal payload del nodo."""
        node = self.get_node(x, y, z)
        if node is None:
            return default
        return node.get(key, default)

    def set_node_value(self, x: float, y: float, z: float, key: str, value: Any) -> bool:
        """Scrive un singolo campo nel payload del nodo."""
        node = self.get_node(x, y, z)
        if node is None:
            return False
        node.set(key, value)
        return True

    # ------------------------------------------------------------------
    #  Gestione archi
    # ------------------------------------------------------------------

    def add_edge(
        self,
        x1: float, y1: float, z1: float,
        x2: float, y2: float, z2: float,
        weight: float = 1.0,
    ) -> Edge:
        """Crea un arco orientato dal nodo (x1,y1,z1) al nodo (x2,y2,z2).

        Se i nodi non esistono vengono creati automaticamente.
        """
        src = self.add_node(x1, y1, z1)
        dst = self.add_node(x2, y2, z2)
        edge = Edge(src, dst, weight)
        self._adj[src.coords].append(edge)
        return edge

    def add_edge_bidi(
        self,
        x1: float, y1: float, z1: float,
        x2: float, y2: float, z2: float,
        weight: float = 1.0,
    ) -> tuple[Edge, Edge]:
        """Crea un arco bidirezionale (due archi orientati opposti, stesso peso)."""
        e1 = self.add_edge(x1, y1, z1, x2, y2, z2, weight)
        e2 = self.add_edge(x2, y2, z2, x1, y1, z1, weight)
        return e1, e2

    def get_edges_from(self, x: float, y: float, z: float) -> list[Edge]:
        """Restituisce tutti gli archi uscenti da un nodo."""
        return list(self._adj.get((float(x), float(y), float(z)), []))

    def get_neighbors(self, x: float, y: float, z: float) -> list[Node]:
        """Restituisce i nodi raggiungibili direttamente dal nodo dato."""
        return [e.target for e in self.get_edges_from(x, y, z)]

    def remove_edge(
        self,
        x1: float, y1: float, z1: float,
        x2: float, y2: float, z2: float,
    ) -> bool:
        """Rimuove il primo arco trovato tra i due nodi. Restituisce True se rimosso."""
        key_src = (float(x1), float(y1), float(z1))
        key_dst = (float(x2), float(y2), float(z2))
        edges = self._adj.get(key_src, [])
        for i, e in enumerate(edges):
            if e.target.coords == key_dst:
                edges.pop(i)
                return True
        return False

    def has_edge(
        self,
        x1: float, y1: float, z1: float,
        x2: float, y2: float, z2: float,
    ) -> bool:
        key_dst = (float(x2), float(y2), float(z2))
        for e in self._adj.get((float(x1), float(y1), float(z1)), []):
            if e.target.coords == key_dst:
                return True
        return False

    # ------------------------------------------------------------------
    #  Utilita'
    # ------------------------------------------------------------------

    def _resolve(self, x: float, y: float, z: float) -> Node:
        """Restituisce il nodo o solleva KeyError."""
        node = self.get_node(x, y, z)
        if node is None:
            raise KeyError(f"Nodo ({x}, {y}, {z}) non trovato nel grafo.")
        return node

    @staticmethod
    def _build_path(came_from: dict[Node, Node | None], target: Node) -> list[Node]:
        path: list[Node] = []
        current: Node | None = target
        while current is not None:
            path.append(current)
            current = came_from.get(current)
        path.reverse()
        return path

    # ------------------------------------------------------------------
    #  Pathfinding: Percorso piu' VICINO (distanza euclidea) — A*
    # ------------------------------------------------------------------

    def shortest_path_euclidean(
        self,
        x1: float, y1: float, z1: float,
        x2: float, y2: float, z2: float,
    ) -> tuple[list[Node], float] | None:
        """Trova il percorso che minimizza la distanza euclidea totale.

        Usa A* con euristica = distanza euclidea verso la destinazione.
        Restituisce (percorso, distanza_totale) oppure None se non raggiungibile.
        """
        start = self._resolve(x1, y1, z1)
        goal = self._resolve(x2, y2, z2)

        if start == goal:
            return ([start], 0.0)

        open_set: list[tuple[float, int, Node]] = []
        counter = 0
        g_score: dict[Node, float] = {start: 0.0}
        came_from: dict[Node, Node | None] = {start: None}

        heapq.heappush(open_set, (start.distance_to(goal), counter, start))

        while open_set:
            _, _, current = heapq.heappop(open_set)

            if current == goal:
                return (self._build_path(came_from, goal), g_score[goal])

            for edge in self._adj.get(current.coords, []):
                neighbor = edge.target
                tentative = g_score[current] + current.distance_to(neighbor)
                if tentative < g_score.get(neighbor, float("inf")):
                    g_score[neighbor] = tentative
                    came_from[neighbor] = current
                    f = tentative + neighbor.distance_to(goal)
                    counter += 1
                    heapq.heappush(open_set, (f, counter, neighbor))

        return None

    # ------------------------------------------------------------------
    #  Pathfinding: Percorso piu' VELOCE/ECONOMICO (peso minimo) — Dijkstra
    # ------------------------------------------------------------------

    def shortest_path_weighted(
        self,
        x1: float, y1: float, z1: float,
        x2: float, y2: float, z2: float,
    ) -> tuple[list[Node], float] | None:
        """Trova il percorso con somma minima dei pesi degli archi (Dijkstra).

        Restituisce (percorso, costo_totale) oppure None se non raggiungibile.
        """
        start = self._resolve(x1, y1, z1)
        goal = self._resolve(x2, y2, z2)

        if start == goal:
            return ([start], 0.0)

        dist: dict[Node, float] = {start: 0.0}
        came_from: dict[Node, Node | None] = {start: None}
        counter = 0
        pq: list[tuple[float, int, Node]] = [(0.0, counter, start)]

        while pq:
            d, _, current = heapq.heappop(pq)

            if current == goal:
                return (self._build_path(came_from, goal), dist[goal])

            if d > dist.get(current, float("inf")):
                continue

            for edge in self._adj.get(current.coords, []):
                neighbor = edge.target
                nd = d + edge.weight
                if nd < dist.get(neighbor, float("inf")):
                    dist[neighbor] = nd
                    came_from[neighbor] = current
                    counter += 1
                    heapq.heappush(pq, (nd, counter, neighbor))

        return None

    # ------------------------------------------------------------------
    #  Pathfinding: Percorso piu' VELOCE/ECONOMICO con euristica — A*
    # ------------------------------------------------------------------

    def shortest_path_astar(
        self,
        x1: float, y1: float, z1: float,
        x2: float, y2: float, z2: float,
    ) -> tuple[list[Node], float] | None:
        """A* sui pesi degli archi con euristica euclidea.

        Richiede che i pesi siano >= distanza euclidea per ammissibilita'.
        Restituisce (percorso, costo_totale) oppure None se non raggiungibile.
        """
        start = self._resolve(x1, y1, z1)
        goal = self._resolve(x2, y2, z2)

        if start == goal:
            return ([start], 0.0)

        g: dict[Node, float] = {start: 0.0}
        came_from: dict[Node, Node | None] = {start: None}
        counter = 0
        pq: list[tuple[float, int, Node]] = [
            (start.distance_to(goal), counter, start)
        ]

        while pq:
            _, _, current = heapq.heappop(pq)

            if current == goal:
                return (self._build_path(came_from, goal), g[goal])

            for edge in self._adj.get(current.coords, []):
                neighbor = edge.target
                tentative = g[current] + edge.weight
                if tentative < g.get(neighbor, float("inf")):
                    g[neighbor] = tentative
                    came_from[neighbor] = current
                    f = tentative + neighbor.distance_to(goal)
                    counter += 1
                    heapq.heappush(pq, (f, counter, neighbor))

        return None

    # ------------------------------------------------------------------
    #  Pathfinding: Percorso piu' LENTO/COSTOSO (peso massimo) — DFS
    # ------------------------------------------------------------------

    def longest_path_weighted(
        self,
        x1: float, y1: float, z1: float,
        x2: float, y2: float, z2: float,
        max_visits: int = 1,
    ) -> tuple[list[Node], float] | None:
        """Trova il percorso con somma massima dei pesi degli archi.

        Usa DFS con backtracking. Ogni nodo puo' essere visitato al massimo
        *max_visits* volte per gestire grafi con cicli senza loop infiniti.

        Args:
            max_visits: numero massimo di volte che un nodo puo' comparire
                        nel percorso (default=1, nessun ciclo).

        Restituisce (percorso, costo_totale) oppure None se non raggiungibile.
        """
        start = self._resolve(x1, y1, z1)
        goal = self._resolve(x2, y2, z2)

        if start == goal:
            return ([start], 0.0)

        best_path: list[Node] | None = None
        best_cost = -1.0
        visit_count: dict[Node, int] = {}

        def _dfs(current: Node, path: list[Node], cost: float) -> None:
            nonlocal best_path, best_cost

            if current == goal:
                if cost > best_cost:
                    best_cost = cost
                    best_path = list(path)
                return

            for edge in self._adj.get(current.coords, []):
                neighbor = edge.target
                count = visit_count.get(neighbor, 0)
                if count < max_visits:
                    visit_count[neighbor] = count + 1
                    path.append(neighbor)
                    _dfs(neighbor, path, cost + edge.weight)
                    path.pop()
                    visit_count[neighbor] = count

        visit_count[start] = 1
        _dfs(start, [start], 0.0)

        if best_path is None:
            return None
        return (best_path, best_cost)

    # ------------------------------------------------------------------
    #  Rappresentazione
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return f"Graph(nodes={self.node_count}, edges={self.edge_count})"

    def __contains__(self, item: tuple[float, float, float] | Node) -> bool:
        if isinstance(item, Node):
            return item.coords in self._nodes
        return tuple(float(c) for c in item) in self._nodes
