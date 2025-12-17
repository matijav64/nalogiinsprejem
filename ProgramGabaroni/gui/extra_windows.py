import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from utils import unify_string
from db_manager import DatabaseManager

class ExtraWindow(tk.Toplevel):
    def __init__(self, master, db_manager: DatabaseManager, e_target=None):
        super().__init__(master)
        self.db = db_manager
        self.e_target = e_target
        self.title("Dodatna sestavina")
        
        # Larger window & font
        self.geometry("600x400")
        self.minsize(600,400)
        self.option_add("*Font", ("Segoe UI", 14))

        self.chosen_text = None
        self.chosen_qty = 0
        
        self.bind("<Escape>", lambda e: self.destroy())

        tk.Label(self, text="Kategorija:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        with sqlite3.connect(self.db.db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT DISTINCT category FROM material_types ORDER BY category")
            cats = [r[0] for r in c.fetchall()]
        self.c_cat = ttk.Combobox(self, values=cats, state="readonly", width=25)
        self.c_cat.grid(row=0, column=1, padx=5, pady=5)
        self.c_cat.bind("<<ComboboxSelected>>", self.on_cat_select)
        
        tk.Label(self, text="Podkategorija:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.c_sub = ttk.Combobox(self, values=[], state="readonly", width=25)
        self.c_sub.grid(row=1, column=1, padx=5, pady=5)
        self.c_sub.bind("<<ComboboxSelected>>", self.on_sub_select)
        
        tk.Label(self, text="Izberi LOT:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.c_lot = ttk.Combobox(self, values=[], state="readonly", width=35)
        self.c_lot.grid(row=2, column=1, padx=5, pady=5)
        
        tk.Label(self, text="Količina (opcijsko):").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.e_qty = tk.Entry(self, width=10)
        self.e_qty.grid(row=3, column=1, padx=5, pady=5)
        
        btn = ttk.Button(self, text="Dodaj sestavino", command=self.add_ingredient)
        btn.grid(row=4, column=0, columnspan=2, pady=10)
        btn.bind("<Return>", lambda e: btn.invoke())

    def on_cat_select(self, event):
        cat = unify_string(self.c_cat.get().strip())
        if not cat:
            return
        with sqlite3.connect(self.db.db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT subcategory, code FROM material_types WHERE category=? ORDER BY subcategory", (cat,))
            subs = c.fetchall()
        self.c_sub['values'] = [f"{s[1]} {s[0]}" for s in subs]
        if subs:
            self.c_sub.set(f"{subs[0][1]} {subs[0][0]}")
            self.load_lot_options(cat, subs[0][0])
    
    def on_sub_select(self, event):
        cat = unify_string(self.c_cat.get().strip())
        sub_with_code = self.c_sub.get().strip()
        if " " in sub_with_code:
            sub = " ".join(sub_with_code.split(" ")[1:])
        else:
            sub = sub_with_code
        self.load_lot_options(cat, sub)
    
    def load_lot_options(self, cat, sub):
        lot_options = []
        with sqlite3.connect(self.db.db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT id FROM material_types WHERE category=? AND subcategory=?", (cat, sub))
            mt_row = c.fetchone()
            if mt_row:
                mt_id = mt_row[0]
                c.execute("""
                    SELECT id, generirana_koda, datum_prejema
                    FROM prejeti_materiali
                    WHERE material_type_id=?
                    ORDER BY id DESC
                    LIMIT 3
                """, (mt_id,))
                for r in c.fetchall():
                    lot_options.append(f"{r[0]}) {r[1]} - {r[2]}")
        self.c_lot['values'] = lot_options
        if lot_options:
            self.c_lot.set(lot_options[0])
        else:
            self.c_lot.set("Ni podatkov")
    
    def add_ingredient(self):
        selected_lot = self.c_lot.get().strip()
        if not selected_lot or selected_lot == "Ni podatkov":
            messagebox.showwarning("Opozorilo", "Izberi veljaven LOT!")
            return
        
        qty_str = self.e_qty.get().strip()  # optional
        if qty_str == "":
            qty = 0
        else:
            try:
                qty = float(qty_str)
            except:
                messagebox.showwarning("Opozorilo", "Količina mora biti številka (ali prazno)!")
                return
        
        self.chosen_text = selected_lot
        self.chosen_qty = qty
        self.destroy()

    def chosen_texts(self):
        return (self.chosen_text, self.chosen_qty)
