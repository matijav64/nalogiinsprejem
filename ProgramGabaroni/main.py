import importlib
import sys
import tkinter as tk
from tkinter import messagebox, ttk
from db_manager import DatabaseManager


def ensure_dependencies():
    required = {
        "pandas": "pandas je potreben za izvoz CSV.",
        "reportlab": "reportlab je potreben za izvoz PDF.",
    }

    missing = []
    for module, desc in required.items():
        try:
            importlib.import_module(module)
        except ImportError:
            missing.append((module, desc))

    if missing:
        msg_lines = ["Manjkajoče odvisnosti:"]
        for module, desc in missing:
            msg_lines.append(f"- {module}: {desc}")
        msg_lines.append("")
        msg_lines.append("Namesti jih z ukazom: python -m pip install -r requirements.txt")
        msg_lines.append("ali: conda install -c conda-forge pandas reportlab")
        full_msg = "\n".join(msg_lines)

        print(full_msg, file=sys.stderr)
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Manjkajoče odvisnosti", full_msg)
            root.destroy()
        except Exception:
            pass

        sys.exit(1)

class App(tk.Tk):
    def __init__(self, db_path="sledenje.db"):
        super().__init__()
        self.title("Program Gabaroni – Polna Funkcionalnost")
        
        # Make the main window bigger
        self.geometry("600x800")
        self.minsize(600, 800)

        # Apply a bigger default font to all widgets
        self.option_add("*Font", ("Segoe UI", 14))

        # We will NOT bind <Return> globally to avoid double triggers.
        # self.bind("<Return>", self.on_enter)  <-- REMOVED

        # Bind Escape to close
        self.bind("<Escape>", lambda e: self.destroy())

        self.db_manager = DatabaseManager(db_path)

        lbl_title = tk.Label(self, text="Možnosti:", font=("Segoe UI", 18))
        lbl_title.pack(pady=20)

        # Create a style for bigger TButton
        style = ttk.Style(self)
        style.configure("Menu.TButton", font=("Segoe UI", 14), padding=15)

        btn_frame = tk.Frame(self)
        btn_frame.pack(expand=True, fill="both", padx=40, pady=10)

        def make_menu_button(txt, cmd):
            btn = ttk.Button(btn_frame, text=txt, style="Menu.TButton", command=cmd)
            btn.pack(pady=10, fill="x")
            # Bind <Return> so that pressing Enter when this button has focus
            # calls cmd exactly once, with no global <Return> binding to double-fire
            btn.bind("<Return>", lambda e: btn.invoke())
            return btn
        
        make_menu_button("Dodaj prejeti material", self.open_add_material)
        make_menu_button("Dodaj delovni nalog", self.open_add_nalog)
        make_menu_button("Izpiši prejete materiale", self.open_show_materials)
        make_menu_button("Izpiši delovne naloge", self.open_show_nalogi)
        make_menu_button("Prikaži stanje zaloge", self.open_show_stock)
        make_menu_button("Nastavi trenutno stanje zaloge", self.open_set_stock)
        make_menu_button("Uredi kategorije", self.open_edit_categories)
        make_menu_button("Izhod", self.destroy)

    # We no longer have on_enter() at the root level

    def open_add_material(self):
        from gui.add_material import AddMaterialWindow
        AddMaterialWindow(self, self.db_manager)

    def open_add_nalog(self):
        from gui.add_nalog import AddNalogWindow
        AddNalogWindow(self, self.db_manager)

    def open_show_materials(self):
        from gui.show_materials import ShowMaterialsWindow
        ShowMaterialsWindow(self, self.db_manager)

    def open_show_nalogi(self):
        from gui.show_nalogi import ShowNalogiWindow
        ShowNalogiWindow(self, self.db_manager)

    def open_show_stock(self):
        from gui.show_stock import ShowStockWindow
        ShowStockWindow(self, self.db_manager)

    def open_set_stock(self):
        from gui.set_stock import SetStockWindow
        SetStockWindow(self, self.db_manager)

    def open_edit_categories(self):
        from gui.edit_categories import EditCategoriesWindow
        EditCategoriesWindow(self, self.db_manager)

if __name__ == "__main__":
    ensure_dependencies()
    app = App("sledenje.db")
    app.mainloop()
