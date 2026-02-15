"""Tema grafico condiviso per tutti gli esempi Tkinter."""


class Colors:
    BG = "#1a1b26"
    BG_SECONDARY = "#24283b"
    BG_CARD = "#2f3348"
    SURFACE = "#3b3f57"
    ACCENT = "#7aa2f7"
    ACCENT_HOVER = "#89b4fa"
    GREEN = "#9ece6a"
    RED = "#f7768e"
    ORANGE = "#ff9e64"
    YELLOW = "#e0af68"
    PURPLE = "#bb9af7"
    CYAN = "#7dcfff"
    TEXT = "#c0caf5"
    TEXT_DIM = "#565f89"
    TEXT_MUTED = "#414868"
    BORDER = "#3b3f57"
    NODE_DEFAULT = "#7aa2f7"
    NODE_START = "#9ece6a"
    NODE_END = "#f7768e"
    NODE_PATH = "#ff9e64"
    EDGE_DEFAULT = "#3b3f57"
    EDGE_PATH = "#ff9e64"


class Fonts:
    TITLE = ("Helvetica Neue", 18, "bold")
    HEADING = ("Helvetica Neue", 13, "bold")
    BODY = ("Helvetica Neue", 11)
    SMALL = ("Helvetica Neue", 10)
    MONO = ("SF Mono", 10)
    MONO_SMALL = ("SF Mono", 9)
    NODE_LABEL = ("Helvetica Neue", 9, "bold")


class Sizes:
    NODE_RADIUS = 18
    NODE_RADIUS_HOVER = 22
    EDGE_WIDTH = 2
    EDGE_PATH_WIDTH = 3
    PADDING = 16
    CARD_RADIUS = 8
    BUTTON_PADX = 20
    BUTTON_PADY = 8


def style_button(btn, color=Colors.ACCENT, hover=Colors.ACCENT_HOVER):
    """Applica stile moderno a un bottone tk."""
    btn.configure(
        bg=color,
        fg="#1a1b26",
        activebackground=hover,
        activeforeground="#1a1b26",
        relief="flat",
        font=Fonts.BODY,
        cursor="hand2",
        padx=Sizes.BUTTON_PADX,
        pady=Sizes.BUTTON_PADY,
        bd=0,
        highlightthickness=0,
    )
    btn.bind("<Enter>", lambda e: btn.configure(bg=hover))
    btn.bind("<Leave>", lambda e: btn.configure(bg=color))


def style_frame(frame, bg=Colors.BG):
    """Applica sfondo a un frame."""
    frame.configure(bg=bg)
