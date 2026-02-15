
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from smartgraph.node import Node


class Edge:
    
    __slots__ = ("source", "target", "weight")

    def __init__(self, source: Node, target: Node, weight: float = 1.0):
        if weight < 0:
            raise ValueError("Il peso dell'arco non puo' essere negativo.")
        self.source = source
        self.target = target
        self.weight = float(weight)

    def __repr__(self) -> str:
        return f"Edge({self.source} -> {self.target}, w={self.weight})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Edge):
            return NotImplemented
        return (
            self.source == other.source
            and self.target == other.target
            and self.weight == other.weight
        )

    def __hash__(self) -> int:
        return hash((self.source, self.target, self.weight))
