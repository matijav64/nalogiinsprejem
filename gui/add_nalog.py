import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from utils import unify_string, parse_datum
from db_manager import DatabaseManager
from gui.extra_windows import ExtraWindow

class AddNalogWindow(tk.Toplevel):
    def __init__(self, master, db_manager: DatabaseManager, nalog_id=None):
        super().__init__(master)
        self.db = db_manager
        self.nalog_id = nalog_id  # None = new, otherwise editing

        self.title("Uredi delovni nalog" if nalog_id else "Dodaj delovni nalog")
        # Larger window
        self.geometry("900x700")
        self.minsize(900, 700)
        self.option_add("*Font", ("Segoe UI", 14))

        style = ttk.Style(self)
        style.configure("TButton", font=("Segoe UI", 14), padding=10)
        style.configure("TLabel", font=("Segoe UI", 14))
        style.configure("TEntry", font=("Segoe UI", 14))

        # Only bind Escape to close, no global <Return> to avoid double triggers
        self.bind("<Escape>", lambda e: self.destroy())

        # Old quantity for difference approach
        self.old_qty = 0.0
        self.old_lot_id = None
        self.moka_category = "Moka"

        row = 0

        tk.Label(self, text="Datum dela (ddmmYYYY):").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.e_datum = tk.Entry(self, width=20)
        self.e_datum.grid(row=row, column=1, padx=5, pady=5)
        row += 1

        tk.Label(self, text="Podkategorija (Moka):").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        subs = self.db.get_subcategories(self.moka_category)
        self.c_sub = ttk.Combobox(self, values=[f"{s[1]} {s[0]}" for s in subs], state="readonly", width=25)
        self.c_sub.grid(row=row, column=1, padx=5, pady=5)
        self.c_sub.bind("<<ComboboxSelected>>", self.on_sub_select)
        row += 1

        tk.Label(self, text="Zadnji 3 vnosi (Moka):").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.c_mat = ttk.Combobox(self, values=[], state="readonly", width=50)
        self.c_mat.grid(row=row, column=1, padx=5, pady=5)
        row += 1

        tk.Label(self, text="Oblika izdelka:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        shapes = [
            ("1) Široki rezanci", "ŠR"),
            ("2) Jušni rezanci", "JR"),
            ("3) Špageti 3", "ŠP3"),
            ("4) Špageti 5", "ŠP5"),
            ("5) Svedri", "SV"),
            ("6) Zmešančki", "Z"),
            ("7) Rožice", "R"),
            ("8) Školjke", "ŠK"),
            ("9) Peresniki", "PR"),
            ("10) Kodrčki", "K")
        ]
        self.c_shape = ttk.Combobox(self, values=[f"{n} - {abbr}" for n, abbr in shapes],
                                    state="readonly", width=35)
        self.c_shape.grid(row=row, column=1, padx=5, pady=5)
        row += 1

        tk.Label(self, text="Količina:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.e_kol = tk.Entry(self, width=10)
        self.e_kol.grid(row=row, column=1, padx=5, pady=5)
        row += 1

        tk.Label(self, text="Dodatne sestavine:").grid(row=row, column=0, sticky="ne", padx=5, pady=5)
        self.ingredients_frame = tk.Frame(self)
        self.ingredients_frame.grid(row=row, column=1, sticky="w", padx=5, pady=5)
        self.ingredients = []
        row += 1

        btn_add_ing = ttk.Button(self, text="Dodaj sestavino", command=self.add_ingredient)
        btn_add_ing.grid(row=row, column=1, sticky="w", padx=5, pady=5)
        btn_add_ing.bind("<Return>", lambda e: btn_add_ing.invoke())
        row += 1

        # Frame that spans columns to center the Save/Cancel
        btn_frame = tk.Frame(self)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=15)
        # Optionally force a width to center
        btn_frame.config(width=400)

        btn_save = ttk.Button(btn_frame, text="Shrani nalog", command=self.save_nalog)
        btn_save.pack(side="left", padx=10)
        btn_save.bind("<Return>", lambda e: btn_save.invoke())

        btn_cancel = ttk.Button(btn_frame, text="Prekliči", command=self.destroy)
        btn_cancel.pack(side="left", padx=10)
        btn_cancel.bind("<Return>", lambda e: btn_cancel.invoke())

        if self.nalog_id:
            self.fill_data()

    def on_sub_select(self, event):
        val = self.c_sub.get().strip()
        parts = val.split(" ", 1)
        if len(parts) < 2:
            sub_name = val
        else:
            sub_name = parts[1]
        self.load_lot_options(sub_name)

    def load_lot_options(self, sub_name):
        combos = []
        with sqlite3.connect(self.db.db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT id FROM material_types WHERE category=? AND subcategory=?", (self.moka_category, sub_name))
            mt_row = c.fetchone()
            if mt_row:
                mt_id = mt_row[0]
                c.execute("""
                    SELECT id, generirana_koda, datum_prejema,
                           (SELECT name FROM suppliers WHERE id = supplier_id)
                    FROM prejeti_materiali
                    WHERE material_type_id=?
                    ORDER BY id DESC
                    LIMIT 3
                """, (mt_id,))
                for r in c.fetchall():
                    supplier_name = r[3] if r[3] else "??"
                    combos.append(f"{r[0]}) {r[1]} - {r[2]} ({supplier_name})")
        self.c_mat['values'] = combos
        if combos:
            self.c_mat.set(combos[0])
        else:
            self.c_mat.set("Ni podatkov")

    def add_ingredient(self):
        extra = ExtraWindow(self, self.db, None)
        self.wait_window(extra)
        ing_text, ing_qty = extra.chosen_texts()
        if ing_text:
            self.ingredients.append((ing_text, ing_qty))
            row_frame = tk.Frame(self.ingredients_frame)
            row_frame.pack(anchor="w", fill="x")
            lbl = tk.Label(row_frame, text=f"{ing_text} (qty: {ing_qty})")
            lbl.pack(side="left", padx=3)
            def remove_ing():
                self.ingredients.remove((ing_text, ing_qty))
                row_frame.destroy()
            btn_x = ttk.Button(row_frame, text="X", command=remove_ing)
            btn_x.pack(side="right", padx=3)

    def fill_data(self):
        with sqlite3.connect(self.db.db_path) as conn:
            c = conn.cursor()
            c.execute("""
                SELECT datum_dela, izbrani_lot, nova_oblika, kolicina, nov_lot, lot_prejsnji_id
                FROM delovni_nalog
                WHERE id=?
            """, (self.nalog_id,))
            rec = c.fetchone()
        if not rec:
            messagebox.showerror("Napaka", "Delovni nalog ni najden!")
            self.destroy()
            return

        try:
            dt = datetime.strptime(rec[0], "%Y-%m-%d")
            self.e_datum.insert(0, dt.strftime("%d%m%Y"))
        except:
            self.e_datum.insert(0, rec[0])
        if rec[2]:
            self.c_shape.set(rec[2])
        self.e_kol.insert(0, str(rec[3]))
        self.old_qty = rec[3] if rec[3] else 0
        if rec[1]:
            self.c_mat.set(rec[1])
        if rec[5]:
            self.old_lot_id = rec[5]

        chosen_lot = rec[1]
        if chosen_lot and ")" in chosen_lot:
            try:
                after_paren = chosen_lot.split(") ")[1]
                code_part = after_paren.split("-")[0].strip()
                with sqlite3.connect(self.db.db_path) as conn:
                    c = conn.cursor()
                    c.execute("SELECT subcategory FROM material_types WHERE category=? AND code=?",
                              (self.moka_category, code_part))
                    row_sub = c.fetchone()
                if row_sub:
                    subcat = row_sub[0]
                    self.c_sub.set(f"{code_part} {subcat}")
                    self.load_lot_options(subcat)
            except:
                pass

        with sqlite3.connect(self.db.db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT sestavina, kolicina FROM delovni_nalog_sestavine WHERE delovni_nalog_id=?",
                      (self.nalog_id,))
            rows = c.fetchall()
        for row in rows:
            ing_text, ing_qty = row[0], row[1]
            self.ingredients.append((ing_text, ing_qty))
            row_frame = tk.Frame(self.ingredients_frame)
            row_frame.pack(anchor="w", fill="x")
            lbl = tk.Label(row_frame, text=f"{ing_text} (qty: {ing_qty})")
            lbl.pack(side="left", padx=3)
            def remove_ing(t=ing_text, q=ing_qty, fr=row_frame):
                self.ingredients.remove((t, q))
                fr.destroy()
            btn_x = ttk.Button(row_frame, text="X", command=remove_ing)
            btn_x.pack(side="right", padx=3)

    def save_nalog(self):
        # The rest of your saving logic (stock update, etc.)
        ...
