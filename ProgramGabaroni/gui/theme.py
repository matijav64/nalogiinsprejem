import tkinter as tk
from tkinter import ttk


PALETTE = {
    "bg": "#F5F7FB",
    "bg_alt": "#E8ECF4",
    "text": "#1E2A3B",
    "muted": "#5A6B82",
    "accent": "#2F5CE5",
    "accent_hover": "#2449B9",
    "accent_light": "#D9E2FF",
    "danger": "#E5484D",
}


def apply_theme(root: tk.Tk | tk.Toplevel) -> ttk.Style:
    root.configure(bg=PALETTE["bg"])
    root.option_add("*Font", ("Segoe UI", 12))
    root.option_add("*Background", PALETTE["bg"])
    root.option_add("*Foreground", PALETTE["text"])
    root.option_add("*Label.Background", PALETTE["bg"])
    root.option_add("*Label.Foreground", PALETTE["text"])
    root.option_add("*Entry.Background", "#FFFFFF")
    root.option_add("*Entry.Foreground", PALETTE["text"])
    root.option_add("*Listbox.Background", "#FFFFFF")
    root.option_add("*Listbox.Foreground", PALETTE["text"])

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure("TFrame", background=PALETTE["bg"])
    style.configure("TLabel", background=PALETTE["bg"], foreground=PALETTE["text"])
    style.configure("Muted.TLabel", foreground=PALETTE["muted"])
    style.configure("Header.TLabel", font=("Segoe UI", 18, "bold"))
    style.configure("Subheader.TLabel", font=("Segoe UI", 14, "bold"))
    style.configure(
        "TButton",
        padding=(12, 8),
        background=PALETTE["accent"],
        foreground="#FFFFFF",
        font=("Segoe UI", 11, "bold"),
        borderwidth=0,
    )
    style.map(
        "TButton",
        background=[
            ("active", PALETTE["accent_hover"]),
            ("pressed", PALETTE["accent_hover"]),
            ("disabled", PALETTE["bg_alt"]),
        ],
        foreground=[("disabled", PALETTE["muted"])],
    )
    style.configure("Secondary.TButton", background=PALETTE["bg_alt"], foreground=PALETTE["text"])
    style.map(
        "Secondary.TButton",
        background=[("active", "#DDE3EF"), ("pressed", "#DDE3EF")],
    )
    style.configure(
        "Danger.TButton",
        background=PALETTE["danger"],
        foreground="#FFFFFF",
    )
    style.map(
        "Danger.TButton",
        background=[("active", "#C23A3E"), ("pressed", "#C23A3E")],
    )

    style.configure("TEntry", fieldbackground="#FFFFFF", foreground=PALETTE["text"], padding=6)
    style.configure("TCombobox", fieldbackground="#FFFFFF", foreground=PALETTE["text"], padding=6)
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", "#FFFFFF")],
        selectbackground=[("readonly", PALETTE["accent_light"])],
    )

    style.configure(
        "Treeview",
        background="#FFFFFF",
        fieldbackground="#FFFFFF",
        foreground=PALETTE["text"],
        rowheight=28,
        bordercolor=PALETTE["bg_alt"],
        borderwidth=1,
    )
    style.configure(
        "Treeview.Heading",
        background=PALETTE["bg_alt"],
        foreground=PALETTE["text"],
        font=("Segoe UI", 11, "bold"),
        padding=(6, 6),
    )
    style.map(
        "Treeview",
        background=[("selected", PALETTE["accent_light"])],
        foreground=[("selected", PALETTE["text"])],
    )
    return style
