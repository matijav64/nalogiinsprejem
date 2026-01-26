import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from utils import unify_string
from db_manager import DatabaseManager
from gui.theme import apply_theme

class SetStockWindow(tk.Toplevel):
    def __init__(self, master, db_manager: DatabaseManager):
        super().__init__(master)
        apply_theme(self)
        self.db = db_manager
        self.title("Nastavi trenutno stanje zaloge")

        # Make the window larger
        self.geometry("600x400")
        self.minsize(600, 400)
        self.bind("<Escape>", lambda e: self.destroy())

        tk.Label(self, text="Izberi kategorijo:").grid(row=0, column=0, sticky="e", padx=10, pady=6)
        self.cat_cb = ttk.Combobox(self, state="readonly", width=20)
        self.load_categories()
        self.cat_cb.grid(row=0, column=1, padx=10, pady=6)
        self.cat_cb.bind("<<ComboboxSelected>>", self.update_subcategories)

        tk.Label(self, text="Izberi podkategorijo:").grid(row=1, column=0, sticky="e", padx=10, pady=6)
        self.sub_cb = ttk.Combobox(self, state="readonly", width=20)
        self.sub_cb.grid(row=1, column=1, padx=10, pady=6)

        tk.Label(self, text="Nova količina:").grid(row=2, column=0, sticky="e", padx=10, pady=6)
        self.e_qty = tk.Entry(self, width=10)
        self.e_qty.grid(row=2, column=1, padx=10, pady=6)

        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=18)

        btn_set = ttk.Button(btn_frame, text="Nastavi", command=self.set_stanje)
        btn_set.pack(side="left", padx=5)
        btn_set.bind("<Return>", lambda e: btn_set.invoke())

        btn_cancel = ttk.Button(btn_frame, text="Prekliči", style="Secondary.TButton", command=self.destroy)
        btn_cancel.pack(side="left", padx=5)
        btn_cancel.bind("<Return>", lambda e: btn_cancel.invoke())

        self.update_subcategories(None)

    def load_categories(self):
        with self.db.connect() as conn:
            c = conn.cursor()
            c.execute("SELECT DISTINCT category FROM material_types ORDER BY category")
            categories = [row[0] for row in c.fetchall()]
        self.cat_cb['values'] = categories
        if categories:
            self.cat_cb.current(0)
        else:
            self.cat_cb.set("")

    def update_subcategories(self, event=None):
        cat = self.cat_cb.get().strip()
        subs = self.db.get_subcategories(cat)
        sub_values = [f"{sub} ({code})" for sub, code in subs]
        self.sub_cb['values'] = sub_values
        if sub_values:
            self.sub_cb.current(0)
        else:
            self.sub_cb.set("")

    def set_stanje(self):
        cat = self.cat_cb.get().strip()
        sub = self.sub_cb.get().strip()
        if not cat or not sub:
            messagebox.showerror("Napaka", "Izberi kategorijo in podkategorijo!")
            return

        # sub is e.g. "Durum (IT1)"
        if "(" in sub and ")" in sub:
            sub_name = sub.split("(")[0].strip()
            code = sub.split("(")[1].replace(")", "").strip()
        else:
            messagebox.showerror("Napaka", "Podkategorija ni v pričakovani obliki (ime (koda))!")
            return

        with self.db.connect() as conn:
            c = conn.cursor()
            c.execute("SELECT id FROM material_types WHERE category=? AND subcategory=?", (cat, sub_name))
            row = c.fetchone()
            if not row:
                messagebox.showerror("Napaka", "Izbrana surovina ni najdena v bazi!")
                return
            mt_id = row[0]

        qty_str = unify_string(self.e_qty.get().strip().replace(",", "."))
        if not qty_str:
            messagebox.showerror("Napaka", "Manjka količina!")
            return

        try:
            new_qty = float(qty_str)
        except:
            messagebox.showerror("Napaka", "Količina mora biti decimal!")
            return

        self.db.set_stock(mt_id, new_qty)
        messagebox.showinfo("OK", f"Nastavili {new_qty} za {cat} -> {sub_name}.")
        self.destroy()
