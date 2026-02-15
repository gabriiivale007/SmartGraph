import sys, os, math, tkinter as tk
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from smartgraph import Graph
from theme import Colors, Fonts, Sizes, style_button, style_frame


# ---------------------------------------------------------------------------
#  Dati di esempio: labirinto
# ---------------------------------------------------------------------------

def build_demo_maze() -> Graph:
    g = Graph()

    # Griglia 6x4 — le celle del labirinto
    celle = {
        (0,0): {"nome": "Ingresso",  "tipo": "ingresso"},
        (1,0): {"nome": "Corridoio", "tipo": "corridoio"},
        (2,0): {"nome": "Corridoio", "tipo": "corridoio"},
        (3,0): {"nome": "Trappola",  "tipo": "trappola", "trappola": "frecce"},
        (4,0): {"nome": "Corridoio", "tipo": "corridoio"},
        (5,0): {"nome": "Corridoio", "tipo": "corridoio"},
        (0,1): {"nome": "Corridoio", "tipo": "corridoio"},
        (1,1): {"nome": "Bonus",     "tipo": "bonus", "bonus": "spada"},
        (2,1): {"nome": "Corridoio", "tipo": "corridoio"},
        (3,1): {"nome": "Corridoio", "tipo": "corridoio"},
        (4,1): {"nome": "Corridoio", "tipo": "corridoio"},
        (5,1): {"nome": "Trappola",  "tipo": "trappola", "trappola": "pozzo"},
        (0,2): {"nome": "Corridoio", "tipo": "corridoio"},
        (1,2): {"nome": "Corridoio", "tipo": "corridoio"},
        (2,2): {"nome": "Corridoio", "tipo": "corridoio"},
        (3,2): {"nome": "Bonus",     "tipo": "bonus", "bonus": "chiave"},
        (4,2): {"nome": "Corridoio", "tipo": "corridoio"},
        (5,2): {"nome": "Corridoio", "tipo": "corridoio"},
        (0,3): {"nome": "Corridoio", "tipo": "corridoio"},
        (1,3): {"nome": "Corridoio", "tipo": "corridoio"},
        (2,3): {"nome": "Trappola",  "tipo": "trappola", "trappola": "gas"},
        (3,3): {"nome": "Corridoio", "tipo": "corridoio"},
        (4,3): {"nome": "Corridoio", "tipo": "corridoio"},
        (5,3): {"nome": "Uscita",    "tipo": "uscita"},
    }
    for (x, y), data in celle.items():
        g.add_node(x, y, 0, data)

    # Corridoi (dove non c'e' arco = muro)
    corridoi = [
        # Orizzontali
        (0,0, 1,0), (1,0, 2,0), (3,0, 4,0), (4,0, 5,0),
        (0,1, 1,1), (2,1, 3,1), (3,1, 4,1),
        (0,2, 1,2), (1,2, 2,2), (3,2, 4,2), (4,2, 5,2),
        (0,3, 1,3), (2,3, 3,3), (3,3, 4,3), (4,3, 5,3),
        # Verticali
        (0,0, 0,1), (0,2, 0,3),
        (1,0, 1,1), (1,1, 1,2),
        (2,0, 2,1), (2,2, 2,3),
        (3,1, 3,2), (3,2, 3,3),
        (4,1, 4,2), (4,2, 4,3),
        (5,0, 5,1), (5,2, 5,3),
    ]
    for x1, y1, x2, y2 in corridoi:
        g.add_edge_bidi(x1, y1, 0, x2, y2, 0, weight=1.0)

    return g


# ---------------------------------------------------------------------------
#  Applicazione
# ---------------------------------------------------------------------------

class MazeViewer(tk.Tk):

    CELL_SIZE = 80
    WALL_THICKNESS = 6

    def __init__(self):
        super().__init__()
        self.title("SmartGraph — Visualizzatore Labirinto")
        self.configure(bg=Colors.BG)
        self.geometry("1100x700")
        self.minsize(900, 550)

        self.graph = build_demo_maze()
        self.scale = 1.0
        self.offset_x = 60.0
        self.offset_y = 60.0
        self.hover_node = None

        # Pre-calcola le connessioni per disegno rapido
        self._connections: set[tuple[tuple, tuple]] = set()
        for edge in self.graph.edges:
            a = (int(edge.source.x), int(edge.source.y))
            b = (int(edge.target.x), int(edge.target.y))
            self._connections.add((min(a, b), max(a, b)))

        self._build_ui()
        self._draw()

    # ----- Layout ----------------------------------------------------------

    def _build_ui(self):
        # Sidebar
        self.sidebar = tk.Frame(self, bg=Colors.BG_SECONDARY, width=280)
        self.sidebar.pack(side="right", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(
            self.sidebar, text="Info Labirinto", font=Fonts.TITLE,
            bg=Colors.BG_SECONDARY, fg=Colors.TEXT, anchor="w",
        ).pack(fill="x", padx=16, pady=(20, 8))

        sep = tk.Frame(self.sidebar, bg=Colors.BORDER, height=1)
        sep.pack(fill="x", padx=16, pady=(0, 12))

        self.info_label = tk.Label(
            self.sidebar, text="", font=Fonts.SMALL,
            bg=Colors.BG_SECONDARY, fg=Colors.TEXT_DIM,
            justify="left", anchor="nw", wraplength=250,
        )
        self.info_label.pack(fill="x", padx=16, pady=4)

        self.detail_label = tk.Label(
            self.sidebar, text="Passa il mouse su una cella\nper vedere i dettagli.",
            font=Fonts.MONO_SMALL,
            bg=Colors.BG_CARD, fg=Colors.TEXT,
            justify="left", anchor="nw", wraplength=240,
            padx=12, pady=12, relief="flat",
        )
        self.detail_label.pack(fill="x", padx=16, pady=(12, 4))

        self._update_info()

        # Legenda
        tk.Label(
            self.sidebar, text="Legenda", font=Fonts.HEADING,
            bg=Colors.BG_SECONDARY, fg=Colors.TEXT, anchor="w",
        ).pack(fill="x", padx=16, pady=(24, 8))

        for label, color in [
            ("ingresso", Colors.GREEN),
            ("uscita", Colors.RED),
            ("trappola", Colors.ORANGE),
            ("bonus", Colors.PURPLE),
            ("corridoio", Colors.ACCENT),
        ]:
            row = tk.Frame(self.sidebar, bg=Colors.BG_SECONDARY)
            row.pack(fill="x", padx=16, pady=2)
            dot = tk.Canvas(row, width=14, height=14, bg=Colors.BG_SECONDARY, highlightthickness=0)
            dot.pack(side="left", padx=(0, 8))
            dot.create_rectangle(1, 1, 13, 13, fill=color, outline="")
            tk.Label(row, text=label, font=Fonts.SMALL, bg=Colors.BG_SECONDARY, fg=Colors.TEXT_DIM).pack(side="left")

        # Canvas
        self.canvas = tk.Canvas(self, bg=Colors.BG, highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.canvas.bind("<Motion>", self._on_motion)
        self.canvas.bind("<MouseWheel>", self._on_scroll)
        self.canvas.bind("<Configure>", lambda e: self._draw())

    # ----- Coordinate -> schermo ------------------------------------------

    def _cell_rect(self, x, y):
        cs = self.CELL_SIZE * self.scale
        sx = self.offset_x + x * cs
        sy = self.offset_y + y * cs
        return sx, sy, sx + cs, sy + cs

    # ----- Disegno --------------------------------------------------------

    def _draw(self):
        c = self.canvas
        c.delete("all")
        cs = self.CELL_SIZE * self.scale
        wt = self.WALL_THICKNESS * self.scale

        tipo_color = {
            "ingresso": Colors.GREEN,
            "uscita": Colors.RED,
            "trappola": Colors.ORANGE,
            "bonus": Colors.PURPLE,
            "corridoio": Colors.BG_CARD,
        }

        all_x = [int(n.x) for n in self.graph.nodes]
        all_y = [int(n.y) for n in self.graph.nodes]
        max_gx = max(all_x)
        max_gy = max(all_y)

        # Sfondo muri
        total_w = (max_gx + 1) * cs + wt
        total_h = (max_gy + 1) * cs + wt
        c.create_rectangle(
            self.offset_x - wt/2, self.offset_y - wt/2,
            self.offset_x + total_w - wt/2, self.offset_y + total_h - wt/2,
            fill="#0f0f17", outline="",
        )

        # Celle
        for node in self.graph.nodes:
            gx, gy = int(node.x), int(node.y)
            x1, y1, x2, y2 = self._cell_rect(gx, gy)
            tipo = node.get("tipo", "corridoio")
            color = tipo_color.get(tipo, Colors.BG_CARD)

            is_hover = (gx, gy) == self.hover_node
            pad = wt / 2
            c.create_rectangle(
                x1 + pad, y1 + pad, x2 - pad, y2 - pad,
                fill=color,
                outline=Colors.YELLOW if is_hover else "",
                width=3 if is_hover else 0,
            )

            # Etichetta
            if cs > 50:
                nome = node.get("nome", "")
                c.create_text(
                    (x1 + x2) / 2, (y1 + y2) / 2,
                    text=nome, fill=Colors.TEXT, font=Fonts.NODE_LABEL,
                )

        # Aperture nei muri (corridoi tra celle adiacenti)
        for (a, b) in self._connections:
            ax, ay = a
            bx, by = b

            if ay == by and bx == ax + 1:
                # Corridoio orizzontale: cancella muro verticale
                x1, y1, x2, y2 = self._cell_rect(ax, ay)
                c.create_rectangle(
                    x2 - wt/2, y1 + wt, x2 + wt/2, y2 - wt,
                    fill=Colors.BG_CARD, outline="",
                )
            elif ax == bx and by == ay + 1:
                # Corridoio verticale: cancella muro orizzontale
                x1, y1, x2, y2 = self._cell_rect(ax, ay)
                c.create_rectangle(
                    x1 + wt, y2 - wt/2, x2 - wt, y2 + wt/2,
                    fill=Colors.BG_CARD, outline="",
                )

    # ----- Interazioni ----------------------------------------------------

    def _hit_cell(self, mx, my):
        cs = self.CELL_SIZE * self.scale
        if mx < self.offset_x or my < self.offset_y:
            return None
        gx = int((mx - self.offset_x) / cs)
        gy = int((my - self.offset_y) / cs)
        if self.graph.has_node(gx, gy, 0):
            return (gx, gy)
        return None

    def _on_motion(self, event):
        old = self.hover_node
        self.hover_node = self._hit_cell(event.x, event.y)
        if old != self.hover_node:
            self._draw()
            self._update_detail()

    def _on_scroll(self, event):
        factor = 1.1 if event.delta > 0 else 0.9
        self.scale *= factor
        self.scale = max(0.4, min(3.0, self.scale))
        self._draw()

    # ----- Info panel -----------------------------------------------------

    def _update_info(self):
        g = self.graph
        self.info_label.config(
            text=(
                f"Celle: {g.node_count}    Corridoi: {g.edge_count // 2}\n\n"
                f"Interazioni:\n"
                f"  - Mouse hover: info cella\n"
                f"  - Rotellina: zoom"
            )
        )

    def _update_detail(self):
        if self.hover_node is None:
            self.detail_label.config(text="Passa il mouse su una cella\nper vedere i dettagli.")
            return
        gx, gy = self.hover_node
        node = self.graph.get_node(gx, gy, 0)
        if node is None:
            return
        lines = [f"Posizione: ({gx}, {gy})", ""]
        for k, v in node.data.items():
            lines.append(f"  {k}: {v}")
        neighbors = self.graph.get_neighbors(gx, gy, 0)
        lines.append(f"\nCelle adiacenti: {len(neighbors)}")
        for n in neighbors:
            n_name = n.get("nome", str(n.coords))
            lines.append(f"  -> ({int(n.x)},{int(n.y)}) {n_name}")
        self.detail_label.config(text="\n".join(lines))


if __name__ == "__main__":
    app = MazeViewer()
    app.mainloop()
