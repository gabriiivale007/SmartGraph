"""Modulo che definisce il Nodo (Cella) del grafo 3D."""

from __future__ import annotations

import math
from typing import Any


class Node:
    
    __slots__ = ("x", "y", "z", "data")

    def __init__(self, x: float, y: float, z: float, data: dict[str, Any] | None = None):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.data: dict[str, Any] = data if data is not None else {}

    @property
    def coords(self) -> tuple[float, float, float]:
        """Restituisce la terna di coordinate."""
        return (self.x, self.y, self.z)

    def distance_to(self, other: Node) -> float:
        """Calcola la distanza euclidea 3D verso un altro nodo."""
        return math.sqrt(
            (self.x - other.x) ** 2
            + (self.y - other.y) ** 2
            + (self.z - other.z) ** 2
        )

    def get(self, key: str, default: Any = None) -> Any:
        """Legge un valore dal payload del nodo."""
        return self.data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Scrive un valore nel payload del nodo."""
        self.data[key] = value

    def update(self, values: dict[str, Any]) -> None:
        """Aggiorna il payload con un dizionario di valori."""
        self.data.update(values)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Node):
            return NotImplemented
        return self.coords == other.coords

    def __hash__(self) -> int:
        return hash(self.coords)

    def __repr__(self) -> str:
        return f"Node({self.x}, {self.y}, {self.z})"

    def __str__(self) -> str:
        return f"[{self.x}, {self.y}, {self.z}]"
