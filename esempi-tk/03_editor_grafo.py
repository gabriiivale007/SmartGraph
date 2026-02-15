import sys, os, math, json, tkinter as tk
from tkinter import simpledialog, messagebox
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from smartgraph import Graph, Node
from theme import Colors, Fonts, Sizes, style_button


class MazeEditor(tk.Tk):

    CELL_SIZE = 70
    WALL_THICKNESS = 6
    GRID_COLS = 10
    GRID_ROWS = 8

    def __init__(self):
        super().__init__()
        self.title("SmartGraph — Editor Labirinto")
        self.configure(bg=Colors.BG)
        self.geometry("1250x780")
        self.minsize(1050, 620)

        self.graph = Graph()
        self._hover_cell: tuple | None = None
        self._selected_cell: tuple | None = None

        # Pre-calcola connessioni per disegno rapido
        self._connections: set[tuple[tuple, tuple]] = set()

        self._build_ui()
        self._draw()

    # ----- Layout ---------------------------------------------------------

    def _build_ui(self):
        # Toolbar in alto
        toolbar = tk.Frame(self, bg=Colors.BG_SECONDARY, height=50)
        toolbar.pack(side="top", fill="x")
        toolbar.pack_propagate(False)

        tk.Label(
            toolbar, text="SmartGraph — Editor Labirinto", font=Fonts.TITLE,
            bg=Colors.BG_SECONDARY, fg=Colors.TEXT,
        ).pack(side="left", padx=16)

        # Bottoni toolbar
        btn_defs = [
            ("Cancella tutto", self._clear_all, Colors.RED),
            ("Riempi griglia", self._fill_grid, Colors.ACCENT),
        ]
        for text, cmd, color in reversed(btn_defs):
            b = tk.Button(toolbar, text=text, command=cmd)
            style_button(b, color, color)
            b.configure(pady=4, padx=14, font=Fonts.SMALL)
            b.pack(side="right", padx=(0, 8), pady=10)

        # Contenuto: canvas + sidebar
        content = tk.Frame(self, bg=Colors.BG)
        content.pack(fill="both", expand=True)

        # Sidebar destra
        sidebar = tk.Frame(content, bg=Colors.BG_SECONDARY, width=290)
        sidebar.pack(side="right", fill="y")
        sidebar.pack_propagate(False)

        # Pannello Istruzioni
        tk.Label(
            sidebar, text="Istruzioni", font=Fonts.HEADING,
            bg=Colors.BG_SECONDARY, fg=Colors.TEXT, anchor="w",
        ).pack(fill="x", padx=16, pady=(16, 4))

        self.help_label = tk.Label(
            sidebar, font=Fonts.SMALL, bg=Colors.BG_CARD, fg=Colors.TEXT_DIM,
            justify="left", anchor="nw", wraplength=250, padx=10, pady=10,
            text=(
                "Click su cella vuota: crea cella\n"
                "Click su muro tra celle: apri corridoio\n"
                "Click su cella: seleziona\n"
                "Tasto destro su cella: elimina\n"
                "Tasto destro su corridoio: chiudi"
            ),
        )
        self.help_label.pack(fill="x", padx=16, pady=(0, 12))

        tk.Frame(sidebar, bg=Colors.BORDER, height=1).pack(fill="x", padx=16)

        # Pannello Cella selezionata
        tk.Label(
            sidebar, text="Cella selezionata", font=Fonts.HEADING,
            bg=Colors.BG_SECONDARY, fg=Colors.TEXT, anchor="w",
        ).pack(fill="x", padx=16, pady=(12, 4))

        self.node_info = tk.Label(
            sidebar, text="Nessuna selezione", font=Fonts.MONO_SMALL,
            bg=Colors.BG_CARD, fg=Colors.TEXT, justify="left",
            anchor="nw", wraplength=250, padx=10, pady=10,
        )
        self.node_info.pack(fill="x", padx=16, pady=(0, 8))

        btn_row = tk.Frame(sidebar, bg=Colors.BG_SECONDARY)
        btn_row.pack(fill="x", padx=16, pady=(0, 8))

        b_edit = tk.Button(btn_row, text="Modifica dati", command=self._edit_node_data)
        style_button(b_edit, Colors.PURPLE, "#c9b5fc")
        b_edit.configure(font=Fonts.SMALL, pady=4)
        b_edit.pack(side="left", fill="x", expand=True, padx=(0, 4))

        b_del = tk.Button(btn_row, text="Elimina", command=self._delete_selected)
        style_button(b_del, Colors.RED, "#ff9ab0")
        b_del.configure(font=Fonts.SMALL, pady=4)
        b_del.pack(side="left", fill="x", expand=True, padx=(4, 0))

        tk.Frame(sidebar, bg=Colors.BORDER, height=1).pack(fill="x", padx=16, pady=(4, 0))

        # Pannello Pathfinding
        tk.Label(
            sidebar, text="Risolvi Labirinto", font=Fonts.HEADING,
            bg=Colors.BG_SECONDARY, fg=Colors.TEXT, anchor="w",
        ).pack(fill="x", padx=16, pady=(12, 4))

        self.algo_var = tk.StringVar(value="dijkstra")
        for label, val in [("Euclidea", "euclidean"), ("Dijkstra", "dijkstra"), ("Piu' lungo", "expensive")]:
            rb = tk.Radiobutton(
                sidebar, text=label, variable=self.algo_var, value=val,
                bg=Colors.BG_SECONDARY, fg=Colors.TEXT,
                selectcolor=Colors.BG_CARD, activebackground=Colors.BG_SECONDARY,
                activeforeground=Colors.TEXT, font=Fonts.SMALL,
                anchor="w", highlightthickness=0,
            )
            rb.pack(fill="x", padx=24, pady=1)

        pf_row = tk.Frame(sidebar, bg=Colors.BG_SECONDARY)
        pf_row.pack(fill="x", padx=16, pady=(8, 4))

        self.pf_start_btn = tk.Button(pf_row, text="Set Start", command=self._set_pf_start)
        style_button(self.pf_start_btn, Colors.GREEN, "#b5e892")
        self.pf_start_btn.configure(font=Fonts.SMALL, pady=4)
        self.pf_start_btn.pack(side="left", fill="x", expand=True, padx=(0, 4))

        self.pf_goal_btn = tk.Button(pf_row, text="Set Goal", command=self._set_pf_goal)
        style_button(self.pf_goal_btn, Colors.RED, "#ff9ab0")
        self.pf_goal_btn.configure(font=Fonts.SMALL, pady=4)
        self.pf_goal_btn.pack(side="left", fill="x", expand=True, padx=(4, 0))

        run_pf = tk.Button(sidebar, text="Risolvi", command=self._run_pf)
        style_button(run_pf, Colors.ACCENT, Colors.ACCENT_HOVER)
        run_pf.configure(font=Fonts.SMALL, pady=5)
        run_pf.pack(fill="x", padx=16, pady=(4, 4))

        self.pf_result = tk.Label(
            sidebar, text="", font=Fonts.MONO_SMALL,
            bg=Colors.BG_CARD, fg=Colors.TEXT,
            justify="left", anchor="nw", wraplength=250, padx=10, pady=10,
        )
        self.pf_result.pack(fill="x", padx=16, pady=(0, 16))

        # Stats in basso
        self.stats_label = tk.Label(
            sidebar, text="", font=Fonts.SMALL,
            bg=Colors.BG_SECONDARY, fg=Colors.TEXT_DIM, anchor="w",
        )
        self.stats_label.pack(side="bottom", fill="x", padx=16, pady=12)

        # Canvas
        self.canvas = tk.Canvas(content, bg=Colors.BG, highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.canvas.bind("<ButtonPress-1>", self._on_click)
        self.canvas.bind("<Motion>", self._on_motion)
        self.canvas.bind("<Button-2>", self._on_right_click)
        self.canvas.bind("<Button-3>", self._on_right_click)

        # PF state
        self._pf_start: tuple | None = None
        self._pf_goal: tuple | None = None
        self._pf_path_nodes: set[tuple] = set()
        self._pf_path_edges: set[tuple[tuple, tuple]] = set()

    # ----- Griglia --------------------------------------------------------

    def _cell_rect(self, gx, gy):
        cs = self.CELL_SIZE
        ox = 40
        oy = 20
        sx = ox + gx * cs
        sy = oy + gy * cs
        return sx, sy, sx + cs, sy + cs

    def _pixel_to_grid(self, mx, my):
        cs = self.CELL_SIZE
        ox, oy = 40, 20
        gx = (mx - ox) / cs
        gy = (my - oy) / cs
        return gx, gy

    def _rebuild_connections(self):
        self._connections.clear()
        for edge in self.graph.edges:
            a = (int(edge.source.x), int(edge.source.y))
            b = (int(edge.target.x), int(edge.target.y))
            self._connections.add((min(a, b), max(a, b)))

    # ----- Disegno --------------------------------------------------------

    def _draw(self):
        c = self.canvas
        c.delete("all")
        cs = self.CELL_SIZE
        wt = self.WALL_THICKNESS

        # Griglia di sfondo (punti)
        ox, oy = 40, 20
        for gx in range(self.GRID_COLS + 1):
            for gy in range(self.GRID_ROWS + 1):
                px = ox + gx * cs
                py = oy + gy * cs
                c.create_oval(px-1, py-1, px+1, py+1, fill=Colors.TEXT_MUTED, outline="")

        # Sfondo muri per celle esistenti (bounding box)
        if self.graph.node_count > 0:
            all_x = [int(n.x) for n in self.graph.nodes]
            all_y = [int(n.y) for n in self.graph.nodes]
            min_gx, max_gx = min(all_x), max(all_x)
            min_gy, max_gy = min(all_y), max(all_y)
            rx1, ry1, _, _ = self._cell_rect(min_gx, min_gy)
            _, _, rx2, ry2 = self._cell_rect(max_gx, max_gy)
            c.create_rectangle(
                rx1 - wt/2, ry1 - wt/2, rx2 + wt/2, ry2 + wt/2,
                fill="#0f0f17", outline="",
            )

        tipo_color = {
            "ingresso": Colors.GREEN,
            "uscita": Colors.RED,
            "trappola": Colors.ORANGE,
            "bonus": Colors.PURPLE,
            "corridoio": Colors.BG_CARD,
        }

        # Celle
        for node in self.graph.nodes:
            gx, gy = int(node.x), int(node.y)
            x1, y1, x2, y2 = self._cell_rect(gx, gy)
            tipo = node.get("tipo", "corridoio")

            is_selected = (gx, gy) == self._selected_cell
            is_start = (gx, gy) == self._pf_start
            is_goal = (gx, gy) == self._pf_goal
            is_path = (gx, gy, 0) in self._pf_path_nodes

            if is_start:
                color = Colors.NODE_START
            elif is_goal:
                color = Colors.NODE_END
            elif is_path:
                color = Colors.NODE_PATH
            else:
                color = tipo_color.get(tipo, Colors.BG_CARD)

            pad = wt / 2
            c.create_rectangle(
                x1 + pad, y1 + pad, x2 - pad, y2 - pad,
                fill=color,
                outline=Colors.YELLOW if is_selected else "",
                width=3 if is_selected else 0,
            )

            nome = node.get("nome", f"({gx},{gy})")
            c.create_text((x1+x2)/2, (y1+y2)/2, text=nome, fill=Colors.TEXT, font=Fonts.NODE_LABEL)

        # Aperture nei muri
        for (a, b) in self._connections:
            ax, ay = a
            bx, by = b
            is_pf = (
                ((*a, 0), (*b, 0)) in self._pf_path_edges or
                ((*b, 0), (*a, 0)) in self._pf_path_edges
            )
            fill = Colors.NODE_PATH if is_pf else Colors.BG_CARD

            if ay == by and bx == ax + 1:
                x1, y1, x2, y2 = self._cell_rect(ax, ay)
                c.create_rectangle(x2 - wt/2, y1 + wt, x2 + wt/2, y2 - wt, fill=fill, outline="")
            elif ax == bx and by == ay + 1:
                x1, y1, x2, y2 = self._cell_rect(ax, ay)
                c.create_rectangle(x1 + wt, y2 - wt/2, x2 - wt, y2 + wt/2, fill=fill, outline="")

        self._update_stats()

    # ----- Hit test -------------------------------------------------------

    def _hit_cell(self, mx, my):
        """Restituisce la cella sotto il mouse, oppure None."""
        gxf, gyf = self._pixel_to_grid(mx, my)
        gx, gy = int(gxf), int(gyf)
        if 0 <= gx < self.GRID_COLS and 0 <= gy < self.GRID_ROWS:
            if self.graph.has_node(gx, gy, 0):
                return (gx, gy)
        return None

    def _hit_wall(self, mx, my):
        """Restituisce la coppia di celle adiacenti separate dal muro sotto il mouse."""
        gxf, gyf = self._pixel_to_grid(mx, my)
        gx = int(gxf)
        gy = int(gyf)
        fx = gxf - gx  # frazione nella cella
        fy = gyf - gy
        wt_frac = self.WALL_THICKNESS / self.CELL_SIZE

        # Bordo destro
        if fx > (1 - wt_frac) and 0 <= gy < self.GRID_ROWS:
            a, b = (gx, gy), (gx + 1, gy)
            if self.graph.has_node(*a, 0) and self.graph.has_node(*b, 0):
                return (a, b)
        # Bordo inferiore
        if fy > (1 - wt_frac) and 0 <= gx < self.GRID_COLS:
            a, b = (gx, gy), (gx, gy + 1)
            if self.graph.has_node(*a, 0) and self.graph.has_node(*b, 0):
                return (a, b)
        return None

    # ----- Mouse events ---------------------------------------------------

    def _on_click(self, event):
        cell = self._hit_cell(event.x, event.y)
        if cell:
            self._selected_cell = cell
            self._update_node_info()
            self._draw()
            return

        # Click su muro tra due celle? -> apri corridoio
        wall = self._hit_wall(event.x, event.y)
        if wall:
            a, b = wall
            key = (min(a, b), max(a, b))
            if key not in self._connections:
                self.graph.add_edge_bidi(*a, 0, *b, 0, weight=1.0)
                self._rebuild_connections()
                self._draw()
            return

        # Click su cella vuota della griglia -> crea cella
        gxf, gyf = self._pixel_to_grid(event.x, event.y)
        gx, gy = int(gxf), int(gyf)
        if 0 <= gx < self.GRID_COLS and 0 <= gy < self.GRID_ROWS:
            if not self.graph.has_node(gx, gy, 0):
                self.graph.add_node(gx, gy, 0, {"nome": f"({gx},{gy})", "tipo": "corridoio"})
                self._draw()

    def _on_motion(self, event):
        old = self._hover_cell
        self._hover_cell = self._hit_cell(event.x, event.y)
        if old != self._hover_cell:
            self._draw()

    def _on_right_click(self, event):
        # Click destro su cella -> elimina
        cell = self._hit_cell(event.x, event.y)
        if cell:
            gx, gy = cell
            self.graph.remove_node(gx, gy, 0)
            self._rebuild_connections()
            if self._selected_cell == cell:
                self._selected_cell = None
            self._pf_path_nodes.discard((gx, gy, 0))
            if self._pf_start == cell:
                self._pf_start = None
            if self._pf_goal == cell:
                self._pf_goal = None
            self._update_node_info()
            self._draw()
            return

        # Click destro su corridoio -> chiudi (rimuovi arco)
        wall = self._hit_wall(event.x, event.y)
        if wall:
            a, b = wall
            key = (min(a, b), max(a, b))
            if key in self._connections:
                self.graph.remove_edge(*a, 0, *b, 0)
                self.graph.remove_edge(*b, 0, *a, 0)
                self._rebuild_connections()
                self._draw()

    # ----- Azioni ---------------------------------------------------------

    def _fill_grid(self):
        """Riempi la griglia con tutte le celle senza corridoi."""
        for gy in range(self.GRID_ROWS):
            for gx in range(self.GRID_COLS):
                if not self.graph.has_node(gx, gy, 0):
                    self.graph.add_node(gx, gy, 0, {"nome": f"({gx},{gy})", "tipo": "corridoio"})
        self._draw()

    def _edit_node_data(self):
        if not self._selected_cell:
            return
        gx, gy = self._selected_cell
        node = self.graph.get_node(gx, gy, 0)
        if not node:
            return
        current_json = json.dumps(node.data, indent=2, ensure_ascii=False)
        new_json = simpledialog.askstring(
            "Modifica dati cella", "JSON della cella:",
            initialvalue=current_json,
        )
        if new_json is None:
            return
        try:
            new_data = json.loads(new_json)
        except json.JSONDecodeError:
            messagebox.showerror("Errore", "JSON non valido.")
            return
        node.data = new_data
        self._update_node_info()
        self._draw()

    def _delete_selected(self):
        if not self._selected_cell:
            return
        gx, gy = self._selected_cell
        self.graph.remove_node(gx, gy, 0)
        self._rebuild_connections()
        self._selected_cell = None
        self._update_node_info()
        self._draw()

    def _clear_all(self):
        if not messagebox.askyesno("Conferma", "Cancellare tutto il labirinto?"):
            return
        self.graph = Graph()
        self._connections.clear()
        self._selected_cell = None
        self._pf_start = None
        self._pf_goal = None
        self._pf_path_nodes.clear()
        self._pf_path_edges.clear()
        self._update_node_info()
        self._draw()

    # ----- Pathfinding nell'editor ----------------------------------------

    def _set_pf_start(self):
        if self._selected_cell:
            self._pf_start = self._selected_cell
            self._pf_path_nodes.clear()
            self._pf_path_edges.clear()
            self._draw()

    def _set_pf_goal(self):
        if self._selected_cell:
            self._pf_goal = self._selected_cell
            self._pf_path_nodes.clear()
            self._pf_path_edges.clear()
            self._draw()

    def _run_pf(self):
        if not self._pf_start or not self._pf_goal:
            self.pf_result.config(text="Imposta START e GOAL\n(seleziona una cella e\nclicca i bottoni).")
            return
        algo = self.algo_var.get()
        s = (*self._pf_start, 0)
        e = (*self._pf_goal, 0)
        if algo == "euclidean":
            result = self.graph.shortest_path_euclidean(*s, *e)
        elif algo == "dijkstra":
            result = self.graph.shortest_path_weighted(*s, *e)
        else:
            result = self.graph.longest_path_weighted(*s, *e)

        self._pf_path_nodes.clear()
        self._pf_path_edges.clear()

        if result is None:
            self.pf_result.config(text="Nessun percorso trovato!")
        else:
            path, cost = result
            for n in path:
                self._pf_path_nodes.add(n.coords)
            for i in range(len(path)-1):
                self._pf_path_edges.add((path[i].coords, path[i+1].coords))
            coords = [f"({int(n.x)},{int(n.y)})" for n in path]
            self.pf_result.config(text=f"Costo: {cost:.2f}\nCelle: {len(path)}\n\n" + " -> ".join(coords))
        self._draw()

    # ----- Info -----------------------------------------------------------

    def _update_node_info(self):
        if not self._selected_cell:
            self.node_info.config(text="Nessuna selezione")
            return
        gx, gy = self._selected_cell
        node = self.graph.get_node(gx, gy, 0)
        if not node:
            self.node_info.config(text="Nessuna selezione")
            return
        lines = [f"Posizione: ({gx}, {gy})"]
        for k, v in node.data.items():
            lines.append(f"  {k}: {v}")
        neighbors = self.graph.get_neighbors(gx, gy, 0)
        lines.append(f"\nCelle adiacenti: {len(neighbors)}")
        for n in neighbors:
            lines.append(f"  -> ({int(n.x)},{int(n.y)})")
        self.node_info.config(text="\n".join(lines))

    def _update_stats(self):
        g = self.graph
        n_corridoi = len(self._connections)
        pf_info = ""
        if self._pf_start:
            pf_info += f"  S: {self._pf_start}"
        if self._pf_goal:
            pf_info += f"  G: {self._pf_goal}"
        self.stats_label.config(text=f"Celle: {g.node_count}  Corridoi: {n_corridoi}{pf_info}")


if __name__ == "__main__":
    app = MazeEditor()
    app.mainloop()
