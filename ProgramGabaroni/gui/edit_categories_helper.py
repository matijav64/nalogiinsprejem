import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from db_manager import DatabaseManager
from gui.edit_single_raw_material import EditSingleRawMaterialWindow
from gui.theme import apply_theme

class EditRawMaterialsWindow(tk.Toplevel):
    def __init__(self, master, db_manager: DatabaseManager):
        super().__init__(master)
        apply_theme(self)
        self.db = db_manager
        self.title("Uredi surovine (drevo)")
        self.geometry("700x400")
        self.bind("<Escape>", lambda e: self.destroy())
        self.tree = ttk.Treeview(self, show="tree")
        self.tree.pack(fill="both", expand=True)
        frm = ttk.Frame(self)
        frm.pack(fill="x")
        ttk.Button(frm, text="Dodaj kategorijo", command=self.add_cat).pack(side="left", padx=8, pady=8)
        ttk.Button(frm, text="Dodaj podkategorijo", command=self.add_sub).pack(side="left", padx=8, pady=8)
        ttk.Button(frm, text="Uredi izbrano", command=self.edit_sel).pack(side="left", padx=8, pady=8)
        ttk.Button(frm, text="Briši izbrano", style="Danger.TButton", command=self.del_sel).pack(side="left", padx=8, pady=8)
        self.refresh_tree()

    def refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        with sqlite3.connect(self.db.db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT id, category, subcategory, code, slediti FROM material_types ORDER BY category, subcategory")
            rows = c.fetchall()
        cats = {}
        for rid, cat, sub, code, sled in rows:
            cats.setdefault(cat, []).append((rid, sub, code, sled))
        for cat, items in cats.items():
            cat_id = self.tree.insert("", "end", text=cat, open=True)
            for rid, sub, code, sled in items:
                track = "DA" if sled == 1 else "NE"
                self.tree.insert(cat_id, "end", text=f"{sub} (code={code}, sledi={track})", values=(rid,))

    def edit_sel(self):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0], "values")
        if not vals:
            messagebox.showinfo("Info", "Izberi podkategorijo, ne kategorijo.")
            return
        rid = vals[0]
        with sqlite3.connect(self.db.db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT id, category, subcategory, code, slediti FROM material_types WHERE id=?", (rid,))
            record = c.fetchone()
        if record:
            # Pass the full record (id, category, subcategory, code, slediti) as a positional argument.
            EditSingleRawMaterialWindow(self, self.db, record)
            self.refresh_tree()

    def add_cat(self):
        new_cat = simpledialog.askstring("Nova kategorija", "Ime kategorije:")
        if new_cat:
            with sqlite3.connect(self.db.db_path) as conn:
                c = conn.cursor()
                # Here we insert a new category with a default subcategory and code.
                c.execute("INSERT INTO material_types (category, subcategory, code, slediti) VALUES (?, ?, ?, 1)",
                          (new_cat, "defaultSub", "??"))
                conn.commit()
            self.refresh_tree()

    def add_sub(self):
        sel = self.tree.selection()
        if not sel:
            new_cat = simpledialog.askstring("Kategorija?", "Ime kategorije:")
            if new_cat:
                new_sub = simpledialog.askstring("Podkategorija?", "Ime podkategorije:")
                new_code = simpledialog.askstring("Koda?", "Koda (npr. ??):")
                if new_sub and new_code:
                    with sqlite3.connect(self.db.db_path) as conn:
                        c = conn.cursor()
                        c.execute("INSERT INTO material_types (category, subcategory, code, slediti) VALUES (?, ?, ?, 1)",
                                  (new_cat, new_sub, new_code))
                        conn.commit()
            self.refresh_tree()
        else:
            item = sel[0]
            vals = self.tree.item(item, "values")
            if not vals:
                # Selected item is a category, so prompt for a subcategory
                cat = self.tree.item(item, "text")
                new_sub = simpledialog.askstring("Podkategorija?", f"Podkategorija za {cat}:")
                new_code = simpledialog.askstring("Koda?", "Koda (npr. ??):")
                if new_sub and new_code:
                    with sqlite3.connect(self.db.db_path) as conn:
                        c = conn.cursor()
                        c.execute("INSERT INTO material_types (category, subcategory, code, slediti) VALUES (?, ?, ?, 1)",
                                  (cat, new_sub, new_code))
                        conn.commit()
                self.refresh_tree()
            else:
                messagebox.showwarning("Opozorilo", "Izberi kategorijo, ne podkategorijo.")

    def del_sel(self):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0], "values")
        if not vals:
            # If a category is selected, delete all rows with that category
            cat = self.tree.item(sel[0], "text")
            if messagebox.askyesno("Brisanje", f"Brisati celotno kategorijo {cat}?"):
                with sqlite3.connect(self.db.db_path) as conn:
                    c = conn.cursor()
                    c.execute("DELETE FROM material_types WHERE category=?", (cat,))
                    conn.commit()
            self.refresh_tree()
        else:
            rid = vals[0]
            if messagebox.askyesno("Brisanje", "Brisati to surovino?"):
                with sqlite3.connect(self.db.db_path) as conn:
                    c = conn.cursor()
                    c.execute("DELETE FROM material_types WHERE id=?", (rid,))
                    conn.commit()
                self.refresh_tree()

class EditSuppliersWindow(tk.Toplevel):
    def __init__(self, master, db_manager: DatabaseManager):
        super().__init__(master)
        apply_theme(self)
        self.db = db_manager
        self.title("Uredi dobavitelje")
        self.geometry("400x300")
        self.bind("<Escape>", lambda e: self.destroy())
        self.tree = ttk.Treeview(self, columns=("ID", "Ime"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Ime", text="Ime")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.on_double_click)
        self.refresh_tree()
        ttk.Button(self, text="Dodaj dobavitelja", command=self.add_supplier).pack(pady=8)

    def refresh_tree(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        with sqlite3.connect(self.db.db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT id, name FROM suppliers ORDER BY name")
            for row in c.fetchall():
                self.tree.insert("", "end", values=row)

    def on_double_click(self, event):
        item = self.tree.focus()
        if item:
            rec = self.tree.item(item)["values"]
            from gui.edit_supplier import EditSupplierWindow
            EditSupplierWindow(self, self.db, rec[0])
            self.refresh_tree()

    def add_supplier(self):
        name = tk.simpledialog.askstring("Dodaj dobavitelja", "Ime dobavitelja:")
        if name:
            with sqlite3.connect(self.db.db_path) as conn:
                c = conn.cursor()
                c.execute("INSERT INTO suppliers (name) VALUES (?)", (name,))
                conn.commit()
            self.refresh_tree()

class EditCarriersWindow(tk.Toplevel):
    def __init__(self, master, db_manager: DatabaseManager):
        super().__init__(master)
        apply_theme(self)
        self.db = db_manager
        self.title("Uredi prevoznike")
        self.geometry("400x300")
        self.bind("<Escape>", lambda e: self.destroy())
        self.tree = ttk.Treeview(self, columns=("ID", "Ime"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Ime", text="Ime")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.on_double_click)
        self.refresh_tree()
        ttk.Button(self, text="Dodaj prevoznika", command=self.add_carrier).pack(pady=8)

    def refresh_tree(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        with sqlite3.connect(self.db.db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT id, name FROM carriers ORDER BY name")
            for row in c.fetchall():
                self.tree.insert("", "end", values=row)

    def on_double_click(self, event):
        item = self.tree.focus()
        if item:
            rec = self.tree.item(item)["values"]
            from gui.edit_carrier import EditCarrierWindow
            EditCarrierWindow(self, self.db, rec[0])
            self.refresh_tree()

    def add_carrier(self):
        name = tk.simpledialog.askstring("Dodaj prevoznika", "Ime prevoznika:")
        if name:
            with sqlite3.connect(self.db.db_path) as conn:
                c = conn.cursor()
                c.execute("INSERT INTO carriers (name) VALUES (?)", (name,))
                conn.commit()
            self.refresh_tree()

class EditPersonsWindow(tk.Toplevel):
    def __init__(self, master, db_manager: DatabaseManager):
        super().__init__(master)
        apply_theme(self)
        self.db = db_manager
        self.title("Uredi prejemce")
        self.geometry("400x300")
        self.bind("<Escape>", lambda e: self.destroy())
        self.tree = ttk.Treeview(self, columns=("ID", "Ime"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Ime", text="Ime")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.on_double_click)
        self.refresh_tree()
        ttk.Button(self, text="Dodaj prejemca", command=self.add_person).pack(pady=8)

    def refresh_tree(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        with sqlite3.connect(self.db.db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT id, name FROM persons ORDER BY name")
            for row in c.fetchall():
                self.tree.insert("", "end", values=row)

    def on_double_click(self, event):
        item = self.tree.focus()
        if item:
            rec = self.tree.item(item)["values"]
            from gui.edit_person import EditPersonWindow
            EditPersonWindow(self, self.db, rec[0])
            self.refresh_tree()

    def add_person(self):
        name = tk.simpledialog.askstring("Dodaj prejemca", "Ime prejemca:")
        if name:
            with sqlite3.connect(self.db.db_path) as conn:
                c = conn.cursor()
                c.execute("INSERT INTO persons (name) VALUES (?)", (name,))
                conn.commit()
            self.refresh_tree()

class EditShapesWindow(tk.Toplevel):
    def __init__(self, master, db_manager: DatabaseManager):
        super().__init__(master)
        apply_theme(self)
        self.db = db_manager
        self.title("Uredi oblike")
        self.geometry("600x350")
        self.bind("<Escape>", lambda e: self.destroy())
        self.tree = ttk.Treeview(self, columns=("ID", "Ime", "Kratica", "VrstniRed"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Ime", text="Ime")
        self.tree.heading("Kratica", text="Kratica")
        self.tree.heading("VrstniRed", text="Vrstni red")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.edit_shape)

        frm = ttk.Frame(self)
        frm.pack(fill="x")
        ttk.Button(frm, text="Dodaj obliko", command=self.add_shape).pack(side="left", padx=8, pady=8)
        ttk.Button(frm, text="Uredi izbrano", command=self.edit_shape).pack(side="left", padx=8, pady=8)
        ttk.Button(frm, text="Briši izbrano", style="Danger.TButton", command=self.delete_shape).pack(side="left", padx=8, pady=8)
        self.refresh_tree()

    def refresh_tree(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        with sqlite3.connect(self.db.db_path) as conn:
            c = conn.cursor()
            c.execute(
                "SELECT id, name, abbreviation, display_order FROM product_shapes ORDER BY display_order, name"
            )
            for row in c.fetchall():
                self.tree.insert("", "end", values=row)

    def add_shape(self):
        name = simpledialog.askstring("Nova oblika", "Ime oblike:")
        if not name:
            return
        abbreviation = simpledialog.askstring("Kratica", "Kratica (npr. ŠR):")
        if not abbreviation:
            return
        order_str = simpledialog.askstring("Vrstni red", "Vrstni red (številka):")
        if not order_str:
            return
        try:
            order = int(order_str)
        except ValueError:
            messagebox.showerror("Napaka", "Vrstni red mora biti številka.")
            return
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                c = conn.cursor()
                c.execute(
                    "INSERT INTO product_shapes (name, abbreviation, display_order) VALUES (?, ?, ?)",
                    (name, abbreviation, order),
                )
                conn.commit()
        except sqlite3.IntegrityError:
            messagebox.showerror("Napaka", "Oblika ali kratica že obstaja.")
            return
        self.refresh_tree()

    def edit_shape(self, event=None):
        item = self.tree.focus()
        if not item:
            return
        rec = self.tree.item(item)["values"]
        if not rec:
            return
        shape_id, name, abbreviation, display_order = rec
        new_name = simpledialog.askstring("Uredi obliko", "Ime oblike:", initialvalue=name)
        if not new_name:
            return
        new_abbreviation = simpledialog.askstring("Uredi kratico", "Kratica:", initialvalue=abbreviation)
        if not new_abbreviation:
            return
        new_order_str = simpledialog.askstring(
            "Uredi vrstni red", "Vrstni red (številka):", initialvalue=str(display_order)
        )
        if not new_order_str:
            return
        try:
            new_order = int(new_order_str)
        except ValueError:
            messagebox.showerror("Napaka", "Vrstni red mora biti številka.")
            return
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                c = conn.cursor()
                c.execute(
                    "UPDATE product_shapes SET name=?, abbreviation=?, display_order=? WHERE id=?",
                    (new_name, new_abbreviation, new_order, shape_id),
                )
                conn.commit()
        except sqlite3.IntegrityError:
            messagebox.showerror("Napaka", "Oblika ali kratica že obstaja.")
            return
        self.refresh_tree()

    def delete_shape(self):
        item = self.tree.focus()
        if not item:
            return
        rec = self.tree.item(item)["values"]
        if not rec:
            return
        if not messagebox.askyesno("Brisanje", "Brisati izbrano obliko?"):
            return
        shape_id = rec[0]
        with sqlite3.connect(self.db.db_path) as conn:
            c = conn.cursor()
            c.execute("DELETE FROM product_shapes WHERE id=?", (shape_id,))
            conn.commit()
        self.refresh_tree()
