import sys, os, math, tkinter as tk
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from smartgraph import Graph, Node
from theme import Colors, Fonts, Sizes, style_button


# ---------------------------------------------------------------------------
#  Labirinto di esempio
# ---------------------------------------------------------------------------

def build_maze() -> Graph:
    g = Graph()

    # Griglia 7x5
    celle = {}
    for y in range(5):
        for x in range(7):
            nome = f"({x},{y})"
            if (x, y) == (0, 0):
                nome = "Ingresso"
            elif (x, y) == (6, 4):
                nome = "Uscita"
            celle[(x, y)] = nome
            g.add_node(x, y, 0, {"nome": nome})

    # Corridoi
    corridoi = [
        # Riga 0
        (0,0, 1,0), (1,0, 2,0), (3,0, 4,0), (5,0, 6,0),
        # Riga 1
        (0,1, 1,1), (1,1, 2,1), (2,1, 3,1), (4,1, 5,1), (5,1, 6,1),
        # Riga 2
        (0,2, 1,2), (2,2, 3,2), (3,2, 4,2), (5,2, 6,2),
        # Riga 3
        (0,3, 1,3), (1,3, 2,3), (3,3, 4,3), (4,3, 5,3), (5,3, 6,3),
        # Riga 4
        (0,4, 1,4), (2,4, 3,4), (3,4, 4,4), (4,4, 5,4), (5,4, 6,4),
        # Verticali
        (0,0, 0,1), (0,2, 0,3), (0,3, 0,4),
        (1,1, 1,2),
        (2,0, 2,1), (2,2, 2,3), (2,3, 2,4),
        (3,0, 3,1), (3,2, 3,3),
        (4,0, 4,1), (4,2, 4,3), (4,3, 4,4),
        (5,1, 5,2),
        (6,0, 6,1), (6,2, 6,3), (6,3, 6,4),
    ]
    for x1, y1, x2, y2 in corridoi:
        g.add_edge_bidi(x1, y1, 0, x2, y2, 0, weight=1.0)

    return g


# ---------------------------------------------------------------------------
#  App principale
# ---------------------------------------------------------------------------

class MazePathfindingApp(tk.Tk):

    CELL_SIZE = 80
    WALL_THICKNESS = 6

    ALGORITHMS = {
        "Euclidea (Piu' vicino)":   "euclidean",
        "Dijkstra (Piu' veloce)":   "dijkstra",
        "Piu' lungo (DFS)":        "expensive",
    }

    def __init__(self):
        super().__init__()
        self.title("SmartGraph — Risolvi il Labirinto")
        self.configure(bg=Colors.BG)
        self.geometry("1200x750")
        self.minsize(1000, 600)

        self.graph = build_maze()
        self.scale = 1.0
        self.offset_x = 40.0
        self.offset_y = 40.0

        self.start_node: Node | None = None
        self.goal_node: Node | None = None
        self.path_nodes: set[tuple] = set()
        self.path_edges: set[tuple[tuple, tuple]] = set()
        self.algo_var = tk.StringVar(value="dijkstra")
        self.selecting = "start"

        # Pre-calcola connessioni
        self._connections: set[tuple[tuple, tuple]] = set()
        for edge in self.graph.edges:
            a = (int(edge.source.x), int(edge.source.y))
            b = (int(edge.target.x), int(edge.target.y))
            self._connections.add((min(a, b), max(a, b)))

        self._build_ui()
        self._draw()

    # ----- UI -------------------------------------------------------------

    def _build_ui(self):
        # Sidebar
        sidebar = tk.Frame(self, bg=Colors.BG_SECONDARY, width=300)
        sidebar.pack(side="right", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(
            sidebar, text="Risolvi Labirinto", font=Fonts.TITLE,
            bg=Colors.BG_SECONDARY, fg=Colors.TEXT,
        ).pack(fill="x", padx=16, pady=(20, 4))
        tk.Frame(sidebar, bg=Colors.BORDER, height=1).pack(fill="x", padx=16, pady=(0, 16))

        # Istruzioni
        self.instr_label = tk.Label(
            sidebar, text="1. Clicca la cella START (verde)",
            font=Fonts.BODY, bg=Colors.BG_SECONDARY, fg=Colors.GREEN,
            anchor="w",
        )
        self.instr_label.pack(fill="x", padx=16, pady=(0, 12))

        # Selezione algoritmo
        tk.Label(
            sidebar, text="Algoritmo", font=Fonts.HEADING,
            bg=Colors.BG_SECONDARY, fg=Colors.TEXT, anchor="w",
        ).pack(fill="x", padx=16, pady=(8, 4))

        for label, val in self.ALGORITHMS.items():
            rb = tk.Radiobutton(
                sidebar, text=label, variable=self.algo_var, value=val,
                bg=Colors.BG_SECONDARY, fg=Colors.TEXT,
                selectcolor=Colors.BG_CARD, activebackground=Colors.BG_SECONDARY,
                activeforeground=Colors.TEXT, font=Fonts.SMALL,
                anchor="w", highlightthickness=0, bd=0,
            )
            rb.pack(fill="x", padx=24, pady=2)

        # Bottoni
        btn_frame = tk.Frame(sidebar, bg=Colors.BG_SECONDARY)
        btn_frame.pack(fill="x", padx=16, pady=(20, 8))

        self.run_btn = tk.Button(btn_frame, text="Risolvi", command=self._run_pathfinding)
        style_button(self.run_btn, Colors.GREEN, "#b5e892")
        self.run_btn.pack(fill="x", pady=(0, 8))

        self.reset_btn = tk.Button(btn_frame, text="Reset", command=self._reset)
        style_button(self.reset_btn, Colors.SURFACE, Colors.BORDER)
        self.reset_btn.configure(fg=Colors.TEXT, activeforeground=Colors.TEXT)
        self.reset_btn.pack(fill="x")

        # Risultato
        tk.Frame(sidebar, bg=Colors.BORDER, height=1).pack(fill="x", padx=16, pady=(16, 12))
        tk.Label(
            sidebar, text="Risultato", font=Fonts.HEADING,
            bg=Colors.BG_SECONDARY, fg=Colors.TEXT, anchor="w",
        ).pack(fill="x", padx=16, pady=(0, 4))

        self.result_label = tk.Label(
            sidebar, text="Seleziona START e GOAL\npoi clicca 'Risolvi'.",
            font=Fonts.MONO_SMALL, bg=Colors.BG_CARD, fg=Colors.TEXT,
            justify="left", anchor="nw", wraplength=260,
            padx=12, pady=12,
        )
        self.result_label.pack(fill="x", padx=16, pady=4)

        # Canvas
        self.canvas = tk.Canvas(self, bg=Colors.BG, highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.bind("<ButtonPress-1>", self._on_click)
        self.canvas.bind("<MouseWheel>", self._on_scroll)
        self.canvas.bind("<Configure>", lambda e: self._draw())

    # ----- Coordinate -> schermo -----------------------------------------

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

        all_x = [int(n.x) for n in self.graph.nodes]
        all_y = [int(n.y) for n in self.graph.nodes]
        max_gx, max_gy = max(all_x), max(all_y)

        # Sfondo muri
        c.create_rectangle(
            self.offset_x - wt/2, self.offset_y - wt/2,
            self.offset_x + (max_gx+1)*cs + wt/2, self.offset_y + (max_gy+1)*cs + wt/2,
            fill="#0f0f17", outline="",
        )

        # Celle
        for node in self.graph.nodes:
            gx, gy = int(node.x), int(node.y)
            x1, y1, x2, y2 = self._cell_rect(gx, gy)

            is_start = self.start_node and (gx, gy) == (int(self.start_node.x), int(self.start_node.y))
            is_goal = self.goal_node and (gx, gy) == (int(self.goal_node.x), int(self.goal_node.y))
            is_path = (gx, gy, 0) in self.path_nodes

            if is_start:
                color = Colors.NODE_START
            elif is_goal:
                color = Colors.NODE_END
            elif is_path:
                color = Colors.NODE_PATH
            else:
                color = Colors.BG_CARD

            pad = wt / 2
            c.create_rectangle(
                x1 + pad, y1 + pad, x2 - pad, y2 - pad,
                fill=color, outline="", width=0,
            )

            # Etichetta
            if cs > 45:
                nome = node.get("nome", f"({gx},{gy})")
                fg = "#1a1b26" if (is_start or is_goal or is_path) else Colors.TEXT_DIM
                c.create_text((x1+x2)/2, (y1+y2)/2, text=nome, fill=fg, font=Fonts.NODE_LABEL)

        # Aperture nei muri
        for (a, b) in self._connections:
            ax, ay = a
            bx, by = b
            is_path_edge = (
                ((*a, 0), (*b, 0)) in self.path_edges or
                ((*b, 0), (*a, 0)) in self.path_edges
            )
            fill = Colors.NODE_PATH if is_path_edge else Colors.BG_CARD

            if ay == by and bx == ax + 1:
                x1, y1, x2, y2 = self._cell_rect(ax, ay)
                c.create_rectangle(x2 - wt/2, y1 + wt, x2 + wt/2, y2 - wt, fill=fill, outline="")
            elif ax == bx and by == ay + 1:
                x1, y1, x2, y2 = self._cell_rect(ax, ay)
                c.create_rectangle(x1 + wt, y2 - wt/2, x2 - wt, y2 + wt/2, fill=fill, outline="")

    # ----- Interazioni ----------------------------------------------------

    def _hit_cell(self, mx, my):
        cs = self.CELL_SIZE * self.scale
        if mx < self.offset_x or my < self.offset_y:
            return None
        gx = int((mx - self.offset_x) / cs)
        gy = int((my - self.offset_y) / cs)
        node = self.graph.get_node(gx, gy, 0)
        return node

    def _on_click(self, event):
        node = self._hit_cell(event.x, event.y)
        if node is None:
            return

        if self.selecting == "start":
            self.start_node = node
            self.selecting = "goal"
            self.instr_label.config(text="2. Clicca la cella GOAL (rossa)", fg=Colors.RED)
        elif self.selecting == "goal":
            self.goal_node = node
            self.selecting = "done"
            self.instr_label.config(text="3. Clicca 'Risolvi'", fg=Colors.ACCENT)

        self.path_nodes.clear()
        self.path_edges.clear()
        self._draw()

    def _on_scroll(self, event):
        factor = 1.1 if event.delta > 0 else 0.9
        self.scale = max(0.3, min(3.0, self.scale * factor))
        self._draw()

    # ----- Pathfinding ----------------------------------------------------

    def _run_pathfinding(self):
        if not self.start_node or not self.goal_node:
            self.result_label.config(text="Seleziona START e GOAL prima!")
            return

        s = self.start_node.coords
        e = self.goal_node.coords
        algo = self.algo_var.get()

        if algo == "euclidean":
            result = self.graph.shortest_path_euclidean(*s, *e)
            algo_name = "Euclidea (A*)"
            metric = "Distanza"
        elif algo == "dijkstra":
            result = self.graph.shortest_path_weighted(*s, *e)
            algo_name = "Dijkstra"
            metric = "Costo"
        else:
            result = self.graph.longest_path_weighted(*s, *e)
            algo_name = "Piu' lungo (DFS)"
            metric = "Costo"

        self.path_nodes.clear()
        self.path_edges.clear()

        if result is None:
            self.result_label.config(text="Nessun percorso trovato!\nIl labirinto non ha soluzione\nper queste celle.")
        else:
            path, cost = result
            for n in path:
                self.path_nodes.add(n.coords)
            for i in range(len(path) - 1):
                self.path_edges.add((path[i].coords, path[i+1].coords))

            nomi = [f"({int(n.x)},{int(n.y)})" for n in path]
            lines = [
                f"Algoritmo: {algo_name}",
                f"{metric}: {cost:.2f}",
                f"Celle attraversate: {len(path)}",
                "",
                "Percorso:",
                *[f"  {i+1}. {n}" for i, n in enumerate(nomi)],
            ]
            self.result_label.config(text="\n".join(lines))

        self._draw()

    def _reset(self):
        self.start_node = None
        self.goal_node = None
        self.path_nodes.clear()
        self.path_edges.clear()
        self.selecting = "start"
        self.instr_label.config(text="1. Clicca la cella START (verde)", fg=Colors.GREEN)
        self.result_label.config(text="Seleziona START e GOAL\npoi clicca 'Risolvi'.")
        self._draw()


if __name__ == "__main__":
    app = MazePathfindingApp()
    app.mainloop()
