import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime
from utils import unify_string, parse_datum, format_ymd_to_ddmmYYYY
from db_manager import DatabaseManager
from gui.theme import apply_theme

def fetch_suppliers(db_path):
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute("SELECT name FROM suppliers ORDER BY name")
        return [r[0] for r in c.fetchall()]

def fetch_carriers(db_path):
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute("SELECT name FROM carriers ORDER BY name")
        return [r[0] for r in c.fetchall()]

def fetch_persons(db_path):
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute("SELECT name FROM persons ORDER BY name")
        return [r[0] for r in c.fetchall()]

class AddMaterialWindow(tk.Toplevel):
    def __init__(self, master, db_manager: DatabaseManager, material_id=None):
        super().__init__(master)
        apply_theme(self)
        self.db = db_manager
        self.material_id = material_id  # If provided, edit mode
        self.title("Uredi prejeti material" if material_id else "Dodaj prejeti material")
        self.geometry("600x500")
        self.bind("<Escape>", lambda e: self.destroy())
        # Bind Enter so that when a button has focus, it is invoked.
        self.bind("<Return>", self.on_enter)
        row = 0
        tk.Label(self, text="Datum prejema (ddmmYYYY):").grid(row=row, column=0, sticky="e", padx=5, pady=3)
        self.e_datum = tk.Entry(self, width=20)
        self.e_datum.grid(row=row, column=1, padx=5, pady=3)
        row += 1
        tk.Label(self, text="Dobavitelj:").grid(row=row, column=0, sticky="e", padx=5, pady=3)
        self.c_dob = ttk.Combobox(self, values=fetch_suppliers(self.db.db_path), width=25)
        self.c_dob.grid(row=row, column=1, padx=5, pady=3)
        btn_new_supplier = ttk.Button(self, text="Dodaj novega", command=self.add_new_supplier, takefocus=0)
        btn_new_supplier.grid(row=row, column=2, padx=5, pady=3)
        btn_new_supplier.bind("<Return>", lambda e: btn_new_supplier.invoke())
        row += 1
        tk.Label(self, text="Prevoznik:").grid(row=row, column=0, sticky="e", padx=5, pady=3)
        self.c_car = ttk.Combobox(self, values=fetch_carriers(self.db.db_path), width=25)
        self.c_car.grid(row=row, column=1, padx=5, pady=3)
        btn_new_carrier = ttk.Button(self, text="Dodaj novega", command=self.add_new_carrier, takefocus=0)
        btn_new_carrier.grid(row=row, column=2, padx=5, pady=3)
        btn_new_carrier.bind("<Return>", lambda e: btn_new_carrier.invoke())
        row += 1
        tk.Label(self, text="Rok uporabe (ddmmYYYY):").grid(row=row, column=0, sticky="e", padx=5, pady=3)
        self.e_rok = tk.Entry(self, width=20)
        self.e_rok.grid(row=row, column=1, padx=5, pady=3)
        row += 1
        tk.Label(self, text="Stanje embalaže:").grid(row=row, column=0, sticky="e", padx=5, pady=3)
        self.e_emb = tk.Entry(self, width=25)
        self.e_emb.grid(row=row, column=1, padx=5, pady=3)
        self.e_emb.insert(0, "Ok")
        row += 1
        tk.Label(self, text="Stanje skladišča:").grid(row=row, column=0, sticky="e", padx=5, pady=3)
        self.e_sklad = tk.Entry(self, width=25)
        self.e_sklad.grid(row=row, column=1, padx=5, pady=3)
        self.e_sklad.insert(0, "Ok")
        row += 1
        tk.Label(self, text="Reklamacije:").grid(row=row, column=0, sticky="e", padx=5, pady=3)
        self.e_rekl = tk.Entry(self, width=25)
        self.e_rekl.grid(row=row, column=1, padx=5, pady=3)
        self.e_rekl.insert(0, "Ok")
        row += 1
        tk.Label(self, text="Prejemec:").grid(row=row, column=0, sticky="e", padx=5, pady=3)
        self.c_person = ttk.Combobox(self, values=fetch_persons(self.db.db_path), width=25)
        self.c_person.grid(row=row, column=1, padx=5, pady=3)
        btn_new_person = ttk.Button(self, text="Dodaj novega", command=self.add_new_person, takefocus=0)
        btn_new_person.grid(row=row, column=2, padx=5, pady=3)
        btn_new_person.bind("<Return>", lambda e: btn_new_person.invoke())
        row += 1
        tk.Label(self, text="Kategorija:").grid(row=row, column=0, sticky="e", padx=5, pady=3)
        with sqlite3.connect(self.db.db_path) as conn:
            cu = conn.cursor()
            cu.execute("SELECT DISTINCT category FROM material_types ORDER BY category")
            cat_list = [r[0] for r in cu.fetchall()]
        self.c_cat = ttk.Combobox(self, values=cat_list, width=25)
        self.c_cat.grid(row=row, column=1, padx=5, pady=3)
        self.c_cat.bind("<<ComboboxSelected>>", self.on_cat_select)
        self.c_cat.bind("<FocusOut>", self.on_cat_select)
        row += 1
        tk.Label(self, text="Podkategorija:").grid(row=row, column=0, sticky="e", padx=5, pady=3)
        # e.g. "IT1 Durum"
        self.c_sub = ttk.Combobox(self, values=[], width=25)
        self.c_sub.grid(row=row, column=1, padx=5, pady=3)
        row += 1
        tk.Label(self, text="Količina:").grid(row=row, column=0, sticky="e", padx=5, pady=3)
        self.e_kol = tk.Entry(self, width=10)
        self.e_kol.grid(row=row, column=1, padx=5, pady=3)
        row += 1
        btn_save = ttk.Button(self, text="Shrani material", command=self.save_material)
        btn_save.grid(row=row, column=0, columnspan=3, pady=15)
        btn_save.bind("<Return>", lambda e: btn_save.invoke())
        self.configure_autocomplete()
        self.configure_tab_navigation()
        self.update_idletasks()
        self.geometry(f"{self.winfo_reqwidth()}x{self.winfo_reqheight()}")
        self.e_datum.focus_set()
        if self.material_id:
            self.fill_data()

    def on_enter(self, event):
        widget = self.focus_get()
        if isinstance(widget, tk.Button):
            widget.invoke()

    def add_new_supplier(self):
        val = tk.simpledialog.askstring("Nov dobavitelj", "Ime dobavitelja:")
        if val:
            with sqlite3.connect(self.db.db_path) as conn:
                c = conn.cursor()
                c.execute("INSERT OR IGNORE INTO suppliers (name) VALUES (?)", (val,))
                conn.commit()
            self.c_dob['values'] = fetch_suppliers(self.db.db_path)
            self.c_dob._full_values = list(self.c_dob['values'])
            self.c_dob.set(val)

    def add_new_carrier(self):
        val = tk.simpledialog.askstring("Nov prevoznik", "Ime prevoznika:")
        if val:
            with sqlite3.connect(self.db.db_path) as conn:
                c = conn.cursor()
                c.execute("INSERT OR IGNORE INTO carriers (name) VALUES (?)", (val,))
                conn.commit()
            self.c_car['values'] = fetch_carriers(self.db.db_path)
            self.c_car._full_values = list(self.c_car['values'])
            self.c_car.set(val)

    def add_new_person(self):
        val = tk.simpledialog.askstring("Nova oseba", "Ime osebe:")
        if val:
            with sqlite3.connect(self.db.db_path) as conn:
                c = conn.cursor()
                c.execute("INSERT OR IGNORE INTO persons (name) VALUES (?)", (val,))
                conn.commit()
            self.c_person['values'] = fetch_persons(self.db.db_path)
            self.c_person._full_values = list(self.c_person['values'])
            self.c_person.set(val)

    def on_cat_select(self, event):
        cat = unify_string(self.c_cat.get().strip())
        if not cat:
            return
        # Use DISTINCT to avoid duplicate subcategories (e.g., duplicate Blitva)
        with sqlite3.connect(self.db.db_path) as conn:
            cu = conn.cursor()
            cu.execute("SELECT DISTINCT subcategory, code FROM material_types WHERE category=? ORDER BY subcategory", (cat,))
            subs = cu.fetchall()
        self.c_sub['values'] = [f"{s[1]} {s[0]}" for s in subs]
        self.c_sub._full_values = list(self.c_sub['values'])
        if subs and not self.c_sub.get():
            self.c_sub.set(f"{subs[0][1]} {subs[0][0]}")

    def fill_data(self):
        with sqlite3.connect(self.db.db_path) as conn:
            c = conn.cursor()
            c.execute("""
                SELECT datum_prejema, supplier_id, carrier_id, rok_uporabe, embalaza_ok,
                       skladisce_ok, reklamacije, person_id, material_type_id, generirana_koda, kolicina
                FROM prejeti_materiali
                WHERE id=?
            """, (self.material_id,))
            rec = c.fetchone()
        if not rec:
            messagebox.showerror("Napaka", "Zapis ni najden!")
            self.destroy()
            return
        try:
            dt = datetime.strptime(rec[0], "%Y-%m-%d")
            self.e_datum.insert(0, dt.strftime("%d%m%Y"))
        except:
            self.e_datum.insert(0, rec[0])
        self.e_rok.insert(0, rec[3] if rec[3] else "")
        # For editing, we now fill the supplier/carrier/person fields from DB:
        with sqlite3.connect(self.db.db_path) as conn:
            c = conn.cursor()
            if rec[1]:
                c.execute("SELECT name FROM suppliers WHERE id=?", (rec[1],))
                row_sup = c.fetchone()
                if row_sup:
                    self.c_dob.set(row_sup[0])
            if rec[2]:
                c.execute("SELECT name FROM carriers WHERE id=?", (rec[2],))
                row_car = c.fetchone()
                if row_car:
                    self.c_car.set(row_car[0])
            if rec[7]:
                c.execute("SELECT name FROM persons WHERE id=?", (rec[7],))
                row_per = c.fetchone()
                if row_per:
                    self.c_person.set(row_per[0])
            c.execute("SELECT category, subcategory, code FROM material_types WHERE id=?", (rec[8],))
            mt = c.fetchone()
        if mt:
            self.c_cat.set(mt[0])
            self.on_cat_select(None)
            self.c_sub.set(f"{mt[2]} {mt[1]}")
        self.e_kol.insert(0, str(rec[10]))

    def configure_autocomplete(self):
        self._setup_autocomplete(self.c_dob)
        self._setup_autocomplete(self.c_car)
        self._setup_autocomplete(self.c_person)
        self._setup_autocomplete(self.c_cat)
        self._setup_autocomplete(self.c_sub)

    def _setup_autocomplete(self, combobox):
        combobox._full_values = list(combobox.cget("values"))
        combobox._typed_text = ""
        combobox.bind("<KeyPress>", lambda event: self._on_combobox_keypress(event, combobox))
        combobox.bind("<KeyRelease>", lambda event: self._on_combobox_typed(event, combobox))
        combobox.bind("<<ComboboxSelected>>", lambda event: self._on_combobox_selected(event, combobox))
        combobox.bind("<FocusIn>", lambda event: self._on_combobox_focus(event, combobox))

    def _on_combobox_focus(self, event, combobox):
        combobox._typed_text = ""

    def _on_combobox_selected(self, event, combobox):
        combobox._typed_text = ""

    def _on_combobox_keypress(self, event, combobox):
        if event.keysym in {"Left", "Right", "Up", "Down", "Tab", "Return", "Escape"}:
            return
        if event.keysym == "BackSpace":
            combobox._typed_text = combobox._typed_text[:-1]
            return
        if event.char and event.char.isprintable():
            combobox._typed_text += event.char

    def _on_combobox_typed(self, event, combobox):
        if event.keysym in {"BackSpace", "Left", "Right", "Up", "Down", "Tab", "Return", "Escape"}:
            return
        typed = combobox._typed_text.strip() or combobox.get().strip()
        if not typed:
            combobox["values"] = combobox._full_values
            return
        typed_lower = typed.lower()
        matches = [val for val in combobox._full_values if typed_lower in val.lower()]
        if matches:
            combobox["values"] = matches
            self._open_combobox_dropdown(combobox)
        else:
            combobox["values"] = combobox._full_values

    def _open_combobox_dropdown(self, combobox):
        self.after(1, lambda: combobox.event_generate("<Down>"))

    def configure_tab_navigation(self):
        self._tab_order = [
            self.e_datum,
            self.c_dob,
            self.c_car,
            self.e_rok,
            self.c_person,
            self.c_cat,
            self.c_sub,
            self.e_kol,
        ]
        for widget in self._tab_order:
            widget.bind("<Tab>", self._on_tab_press)

    def _on_tab_press(self, event):
        if event.widget in {self.e_datum, self.e_rok}:
            self._auto_fill_year(event.widget)
        try:
            idx = self._tab_order.index(event.widget)
        except ValueError:
            idx = -1
        next_widget = None
        if idx >= 0 and idx + 1 < len(self._tab_order):
            next_widget = self._tab_order[idx + 1]
        if next_widget:
            next_widget.focus_set()
        return "break"

    def _auto_fill_year(self, entry):
        value = entry.get().strip()
        if len(value) == 4 and value.isdigit():
            entry.insert(tk.END, str(datetime.now().year))

    def save_material(self):
        d_val = unify_string(self.e_datum.get().strip())
        cat_val = unify_string(self.c_cat.get().strip())
        sub_val = unify_string(self.c_sub.get().strip())
        dob_val = unify_string(self.c_dob.get().strip())
        car_val = unify_string(self.c_car.get().strip())
        per_val = unify_string(self.c_person.get().strip())
        rok_val = unify_string(self.e_rok.get().strip())
        emb_val = unify_string(self.e_emb.get().strip())
        sklad_val = unify_string(self.e_sklad.get().strip())
        rekl_val = unify_string(self.e_rekl.get().strip())
        kol_str = unify_string(self.e_kol.get().strip().replace(",", "."))
        if not d_val or not cat_val or not sub_val or not dob_val or not per_val or not kol_str:
            messagebox.showerror("Napaka", "Manjkajo polja (datum, kategorija, dobavitelj, prejemec, količina...)")
            return
        try:
            dd, d_fmt = parse_datum(d_val)
        except:
            messagebox.showerror("Napaka", "Napačen datum!")
            return
        try:
            qty = float(kol_str)
        except:
            messagebox.showerror("Napaka", "Količina ni decimal!")
            return
        parts = sub_val.split(" ", 1)
        if len(parts) < 2:
            messagebox.showerror("Napaka", "Podkategorija nima ustreznega formata (npr. 'IT1 Durum')!")
            return
        sub_code = parts[0]
        sub_name = parts[1]
        gen_code = f"{sub_code}-{d_fmt}"
        mt_id = self.db.get_or_create_material_type(cat_val, sub_name, sub_code)

        with sqlite3.connect(self.db.db_path) as conn:
            c = conn.cursor()
            def get_or_create_id(table, name):
                if not name:
                    return None
                c.execute(f"SELECT id FROM {table} WHERE LOWER(name)=LOWER(?)", (name,))
                row = c.fetchone()
                if row:
                    return row[0]
                c.execute(f"INSERT INTO {table} (name) VALUES (?)", (name,))
                return c.lastrowid

            supplier_id = get_or_create_id("suppliers", dob_val)
            person_id = get_or_create_id("persons", per_val)
            carrier_id = get_or_create_id("carriers", car_val) if car_val else None

            if self.material_id:
                # Retrieve old quantity first to adjust stock correctly
                c.execute("SELECT kolicina, material_type_id FROM prejeti_materiali WHERE id=?", (self.material_id,))
                old_row = c.fetchone()
                old_qty = old_row[0] if old_row else 0
                old_mt_id = old_row[1] if old_row else None
                c.execute("""
                    UPDATE prejeti_materiali
                    SET datum_prejema=?,
                        supplier_id=?,
                        carrier_id=?,
                        rok_uporabe=?,
                        embalaza_ok=?,
                        skladisce_ok=?,
                        reklamacije=?,
                        person_id=?,
                        material_type_id=?,
                        generirana_koda=?,
                        kolicina=?
                    WHERE id=?
                """, (dd, supplier_id, carrier_id, rok_val, emb_val, sklad_val, rekl_val,
                      person_id, mt_id, gen_code, qty, self.material_id))
            else:
                c.execute("""
                    INSERT INTO prejeti_materiali
                    (datum_prejema, supplier_id, carrier_id, rok_uporabe, embalaza_ok,
                     skladisce_ok, reklamacije, person_id, material_type_id, generirana_koda, kolicina)
                    VALUES (
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?
                    )
                """, (dd, supplier_id, carrier_id, rok_val, emb_val, sklad_val, rekl_val,
                      person_id, mt_id, gen_code, qty))
            conn.commit()
        # Update stock: if editing, use diff; if new, add entire qty
        if self.material_id:
            if old_mt_id == mt_id:
                diff = qty - old_qty
                self.db.update_stock(mt_id, diff)
            else:
                if old_mt_id is not None:
                    self.db.update_stock(old_mt_id, -old_qty)
                self.db.update_stock(mt_id, qty)
        else:
            self.db.update_stock(mt_id, qty)
        self.clipboard_clear()
        self.clipboard_append(gen_code)
        messagebox.showinfo("Koda", f"Generirana koda: {gen_code}\n(kopirano)")
        self.destroy()
