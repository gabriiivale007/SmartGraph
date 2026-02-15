import sys, os, math, tkinter as tk
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from smartgraph import Graph, Node
from theme import Colors, Fonts, Sizes, style_button


# ---------------------------------------------------------------------------
#  Labirinto di demo
# ---------------------------------------------------------------------------

def build_maze() -> tuple[Graph, dict]:
    g = Graph()

    # Griglia 6x5 con nomi significativi
    layout = {
        "S": (0, 0), "A": (1, 0), "B": (2, 0), "C": (3, 0), "D": (4, 0), "E": (5, 0),
        "F": (0, 1), "G": (1, 1), "H": (2, 1), "I": (3, 1), "J": (4, 1), "K": (5, 1),
        "L": (0, 2), "M": (1, 2), "N": (2, 2), "O": (3, 2), "P": (4, 2), "Q": (5, 2),
        "R": (0, 3), "T": (1, 3), "V": (2, 3), "W": (3, 3), "X": (4, 3), "U": (5, 3),
    }
    for name, (x, y) in layout.items():
        g.add_node(x, y, 0, {"nome": name})

    # Corridoi con pesi variabili (difficolta')
    corridoi = [
        # Riga 0
        ("S", "A", 1), ("A", "B", 2), ("C", "D", 1), ("D", "E", 3),
        # Riga 1
        ("F", "G", 2), ("H", "I", 1), ("I", "J", 4), ("J", "K", 1),
        # Riga 2
        ("L", "M", 1), ("M", "N", 3), ("O", "P", 2), ("P", "Q", 1),
        # Riga 3
        ("R", "T", 2), ("V", "W", 1), ("W", "X", 3), ("X", "U", 1),
        # Verticali
        ("S", "F", 3), ("A", "G", 1), ("B", "H", 2),
        ("C", "I", 1), ("E", "K", 2),
        ("F", "L", 1), ("G", "M", 2), ("H", "N", 1),
        ("I", "O", 3), ("K", "Q", 1),
        ("L", "R", 2), ("N", "V", 1), ("O", "W", 2),
        ("P", "X", 1), ("Q", "U", 3),
    ]
    name_to_c = {n: c for n, c in layout.items()}
    for s, d, w in corridoi:
        g.add_edge_bidi(*name_to_c[s], 0, *name_to_c[d], 0, weight=w)

    return g, layout


# ---------------------------------------------------------------------------
#  App
# ---------------------------------------------------------------------------

class CompareApp(tk.Tk):

    ALGO_CONFIG = [
        ("Euclidea\n(Piu' vicino)", "euclidean", Colors.CYAN),
        ("Dijkstra\n(Piu' veloce)", "dijkstra", Colors.GREEN),
        ("DFS\n(Piu' lungo)", "expensive", Colors.RED),
    ]

    CELL_SIZE = 60
    WALL_THICKNESS = 4

    def __init__(self):
        super().__init__()
        self.title("SmartGraph — Confronto Algoritmi sul Labirinto")
        self.configure(bg=Colors.BG)
        self.geometry("1300x750")
        self.minsize(1100, 600)

        self.graph, self.layout = build_maze()
        self.name_to_coords = {n: c for n, c in self.layout.items()}

        # Pre-calcola connessioni
        self._connections: set[tuple[tuple, tuple]] = set()
        for edge in self.graph.edges:
            a = (int(edge.source.x), int(edge.source.y))
            b = (int(edge.target.x), int(edge.target.y))
            self._connections.add((min(a, b), max(a, b)))

        self.start_name = "S"
        self.goal_name = "U"

        self.results: dict[str, tuple[list[Node], float] | None] = {}
        self._anim_step: dict[str, int] = {}
        self._anim_running = False

        self._build_ui()
        self._run_all()

    def _build_ui(self):
        # Top bar
        top = tk.Frame(self, bg=Colors.BG_SECONDARY, height=56)
        top.pack(side="top", fill="x")
        top.pack_propagate(False)

        tk.Label(top, text="Confronto Algoritmi — Labirinto", font=Fonts.TITLE,
                 bg=Colors.BG_SECONDARY, fg=Colors.TEXT).pack(side="left", padx=16)

        # Start / Goal selector
        sel_frame = tk.Frame(top, bg=Colors.BG_SECONDARY)
        sel_frame.pack(side="right", padx=16)

        tk.Label(sel_frame, text="Start:", font=Fonts.BODY,
                 bg=Colors.BG_SECONDARY, fg=Colors.GREEN).pack(side="left", padx=(0, 4))

        self.start_var = tk.StringVar(value=self.start_name)
        node_names = sorted(self.layout.keys())
        start_menu = tk.OptionMenu(sel_frame, self.start_var, *node_names)
        start_menu.configure(bg=Colors.BG_CARD, fg=Colors.TEXT, font=Fonts.SMALL,
                             highlightthickness=0, activebackground=Colors.SURFACE)
        start_menu.pack(side="left", padx=(0, 12))

        tk.Label(sel_frame, text="Goal:", font=Fonts.BODY,
                 bg=Colors.BG_SECONDARY, fg=Colors.RED).pack(side="left", padx=(0, 4))

        self.goal_var = tk.StringVar(value=self.goal_name)
        goal_menu = tk.OptionMenu(sel_frame, self.goal_var, *node_names)
        goal_menu.configure(bg=Colors.BG_CARD, fg=Colors.TEXT, font=Fonts.SMALL,
                            highlightthickness=0, activebackground=Colors.SURFACE)
        goal_menu.pack(side="left", padx=(0, 12))

        run_btn = tk.Button(sel_frame, text="Calcola", command=self._run_all)
        style_button(run_btn, Colors.ACCENT, Colors.ACCENT_HOVER)
        run_btn.configure(font=Fonts.SMALL, pady=3, padx=12)
        run_btn.pack(side="left")

        anim_btn = tk.Button(sel_frame, text="Anima", command=self._start_animation)
        style_button(anim_btn, Colors.ORANGE, "#ffb88a")
        anim_btn.configure(font=Fonts.SMALL, pady=3, padx=12)
        anim_btn.pack(side="left", padx=(8, 0))

        # 3 colonne
        self.panels_frame = tk.Frame(self, bg=Colors.BG)
        self.panels_frame.pack(fill="both", expand=True)

        self.canvases: dict[str, tk.Canvas] = {}
        self.stat_labels: dict[str, tk.Label] = {}

        for i, (title, key, color) in enumerate(self.ALGO_CONFIG):
            col = tk.Frame(self.panels_frame, bg=Colors.BG)
            col.pack(side="left", fill="both", expand=True, padx=2)

            header = tk.Frame(col, bg=color, height=36)
            header.pack(fill="x")
            header.pack_propagate(False)
            tk.Label(header, text=title, font=Fonts.HEADING, bg=color, fg="#1a1b26",
                     justify="center").pack(expand=True)

            cv = tk.Canvas(col, bg=Colors.BG, highlightthickness=0)
            cv.pack(fill="both", expand=True)
            self.canvases[key] = cv

            stat = tk.Label(col, text="", font=Fonts.MONO_SMALL, bg=Colors.BG_SECONDARY,
                            fg=Colors.TEXT, anchor="w", padx=10, pady=8)
            stat.pack(fill="x")
            self.stat_labels[key] = stat

            cv.bind("<Configure>", lambda e, k=key: self._draw_panel(k))

    # ----- Posizione cella nel pannello -----------------------------------

    def _cell_rect_in_canvas(self, cv: tk.Canvas, gx: int, gy: int):
        w = max(cv.winfo_width(), 1)
        h = max(cv.winfo_height(), 1)
        cs = self.CELL_SIZE

        all_x = [c[0] for c in self.layout.values()]
        all_y = [c[1] for c in self.layout.values()]
        cols = max(all_x) + 1
        rows = max(all_y) + 1
        total_w = cols * cs
        total_h = rows * cs

        ox = (w - total_w) / 2
        oy = (h - total_h) / 2

        sx = ox + gx * cs
        sy = oy + gy * cs
        return sx, sy, sx + cs, sy + cs

    # ----- Disegno pannello singolo ---------------------------------------

    def _draw_panel(self, key: str):
        cv = self.canvases[key]
        cv.delete("all")
        cs = self.CELL_SIZE
        wt = self.WALL_THICKNESS
        algo_color = {k: c for _, k, c in self.ALGO_CONFIG}[key]

        result = self.results.get(key)
        path_nodes: set[tuple] = set()
        path_edges: set[tuple[tuple, tuple]] = set()
        anim_limit = self._anim_step.get(key, 999)

        if result:
            path, cost = result
            shown = path[:anim_limit+1]
            for n in shown:
                path_nodes.add((int(n.x), int(n.y)))
            for i in range(len(shown)-1):
                a = (int(shown[i].x), int(shown[i].y))
                b = (int(shown[i+1].x), int(shown[i+1].y))
                path_edges.add((min(a, b), max(a, b)))

        # Calcola limiti griglia
        all_x = [c[0] for c in self.layout.values()]
        all_y = [c[1] for c in self.layout.values()]
        max_gx, max_gy = max(all_x), max(all_y)

        # Sfondo muri
        rx1, ry1, _, _ = self._cell_rect_in_canvas(cv, 0, 0)
        _, _, rx2, ry2 = self._cell_rect_in_canvas(cv, max_gx, max_gy)
        cv.create_rectangle(rx1 - wt, ry1 - wt, rx2 + wt, ry2 + wt, fill="#0f0f17", outline="")

        start_c = self.name_to_coords.get(self.start_var.get())
        goal_c = self.name_to_coords.get(self.goal_var.get())

        # Celle
        for node in self.graph.nodes:
            gx, gy = int(node.x), int(node.y)
            x1, y1, x2, y2 = self._cell_rect_in_canvas(cv, gx, gy)
            is_start = (gx, gy) == start_c
            is_goal = (gx, gy) == goal_c
            is_path = (gx, gy) in path_nodes

            if is_start:
                c = Colors.GREEN
            elif is_goal:
                c = Colors.RED
            elif is_path:
                c = algo_color
            else:
                c = Colors.SURFACE

            pad = wt / 2
            cv.create_rectangle(x1+pad, y1+pad, x2-pad, y2-pad, fill=c, outline="")
            fg = "#1a1b26" if (is_path or is_start or is_goal) else Colors.TEXT_DIM
            cv.create_text((x1+x2)/2, (y1+y2)/2, text=node.get("nome","?"), fill=fg, font=Fonts.NODE_LABEL)

        # Aperture nei muri
        for (a, b) in self._connections:
            ax, ay = a
            bx, by = b
            is_pf = (a, b) in path_edges or (b, a) in path_edges
            fill = algo_color if is_pf else Colors.SURFACE

            if ay == by and bx == ax + 1:
                x1, y1, x2, y2 = self._cell_rect_in_canvas(cv, ax, ay)
                cv.create_rectangle(x2-wt/2, y1+wt, x2+wt/2, y2-wt, fill=fill, outline="")
            elif ax == bx and by == ay + 1:
                x1, y1, x2, y2 = self._cell_rect_in_canvas(cv, ax, ay)
                cv.create_rectangle(x1+wt, y2-wt/2, x2-wt, y2+wt/2, fill=fill, outline="")

    # ----- Esecuzione algoritmi -------------------------------------------

    def _run_all(self):
        self.start_name = self.start_var.get()
        self.goal_name = self.goal_var.get()
        sc = self.name_to_coords.get(self.start_name)
        gc = self.name_to_coords.get(self.goal_name)
        if not sc or not gc:
            return

        self.results["euclidean"] = self.graph.shortest_path_euclidean(*sc, 0, *gc, 0)
        self.results["dijkstra"] = self.graph.shortest_path_weighted(*sc, 0, *gc, 0)
        self.results["expensive"] = self.graph.longest_path_weighted(*sc, 0, *gc, 0)

        self._anim_step = {k: 999 for k in self.results}
        self._anim_running = False

        for key in self.canvases:
            self._draw_panel(key)
            self._update_stat(key)

    def _update_stat(self, key: str):
        result = self.results.get(key)
        if result is None:
            self.stat_labels[key].config(text="Nessun percorso")
            return
        path, cost = result
        nomi = " -> ".join(n.get("nome","?") for n in path)
        self.stat_labels[key].config(text=f"Costo: {cost:.0f} | Celle: {len(path)} | {nomi}")

    # ----- Animazione -----------------------------------------------------

    def _start_animation(self):
        if self._anim_running:
            return
        self._anim_running = True
        self._anim_step = {k: 0 for k in self.results}
        self._animate_tick()

    def _animate_tick(self):
        if not self._anim_running:
            return
        all_done = True
        for key, result in self.results.items():
            if result is None:
                continue
            path, _ = result
            step = self._anim_step.get(key, 0)
            if step < len(path):
                all_done = False
                self._anim_step[key] = step + 1
            self._draw_panel(key)

        if all_done:
            self._anim_running = False
        else:
            self.after(400, self._animate_tick)


if __name__ == "__main__":
    app = CompareApp()
    app.mainloop()
