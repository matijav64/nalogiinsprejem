import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from utils import unify_string, format_ymd_to_ddmmYYYY
from export_utils import export_data_dialog

class ShowMaterialsWindow(tk.Toplevel):
    def __init__(self, master, db_manager):
        super().__init__(master)
        self.db = db_manager
        self.title("Izpiši prejete materiale")
        self.geometry("1020x600")
        self.bind("<Escape>", lambda e: self.destroy())
        top_frame = tk.Frame(self)
        top_frame.pack(pady=5, fill="x")
        tk.Label(top_frame, text="Iskanje:").grid(row=0, column=0, padx=3, pady=3, sticky="e")
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(top_frame, textvariable=self.search_var, width=30)
        self.search_entry.grid(row=0, column=1, padx=3, pady=3)
        self.search_var.trace_add("write", lambda *args: self.filter_data())
        btn_filter = ttk.Button(top_frame, text="Filtriraj", command=self.filter_data)
        btn_filter.grid(row=0, column=2, padx=5, pady=3)
        btn_filter.bind("<Return>", lambda e: btn_filter.invoke())
        btn_export = ttk.Button(top_frame, text="Izvozi", command=self.open_export_dialog)
        btn_export.grid(row=0, column=3, padx=5, pady=3)
        btn_export.bind("<Return>", lambda e: btn_export.invoke())
        cols = ("ID", "Datum", "Dobavitelj", "Prevoznik", "Rok uporabe", "Emb. stanje", "Skl. stanje", "Reklamacije", "Prejemec", "Generirana koda", "Količina")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.on_double_click)
        self.filter_data()
        self.update_idletasks()
        self.geometry(f"{self.winfo_reqwidth()}x{self.winfo_reqheight()}")

    def filter_data(self, event=None):
        for i in self.tree.get_children():
            self.tree.delete(i)
        search_text = unify_string(self.search_var.get()).casefold()
        query = """
            SELECT pm.id, FORMAT_DATE(pm.datum_prejema), 
                   IFNULL(s.name, '') as supplier,
                   IFNULL(c.name, '') as carrier,
                   FORMAT_DATE(pm.rok_uporabe),
                   pm.embalaza_ok, pm.skladisce_ok, pm.reklamacije,
                   IFNULL(p.name, '') as person,
                   pm.generirana_koda, pm.kolicina
            FROM prejeti_materiali pm
            JOIN material_types mt ON pm.material_type_id = mt.id
            LEFT JOIN suppliers s ON pm.supplier_id = s.id
            LEFT JOIN carriers c ON pm.carrier_id = c.id
            LEFT JOIN persons p ON pm.person_id = p.id
            WHERE 1=1
        """
        params = []
        if search_text:
            query += """
                AND (
                    CASEFOLD(s.name) LIKE ? OR 
                    CASEFOLD(c.name) LIKE ? OR 
                    CASEFOLD(p.name) LIKE ? OR 
                    CASEFOLD(pm.generirana_koda) LIKE ? OR 
                    CASEFOLD(FORMAT_DATE(pm.datum_prejema)) LIKE ? OR
                    CASEFOLD(FORMAT_DATE(pm.rok_uporabe)) LIKE ?
                )
            """
            pattern = f"%{search_text}%"
            params.extend([pattern]*6)
        query += " ORDER BY pm.id ASC"
        with sqlite3.connect(self.db.db_path) as conn:
            conn.create_function("FORMAT_DATE", 1, format_ymd_to_ddmmYYYY)
            conn.create_function("CASEFOLD", 1, lambda s: s.casefold() if s else "")
            c = conn.cursor()
            c.execute(query, params)
            rows = c.fetchall()
        for row in rows:
            self.tree.insert("", "end", values=row)

    def open_export_dialog(self):
        data = [list(self.tree.item(child)["values"]) for child in self.tree.get_children()]
        if not data:
            messagebox.showwarning("Opozorilo", "Ni podatkov za izvoz!")
            return
        headers = ["ID", "datum_prejema", "dobavitelj", "prevoznik", "rok_uporabe", "embalaza_ok", "skladisce_ok", "reklamacije", "prejemec", "generirana_koda", "kolicina"]
        export_data_dialog(headers, data, "prejeti_materiali", "Materials")

    def on_double_click(self, event):
        item = self.tree.focus()
        if item:
            rec = self.tree.item(item)["values"]
            from gui.add_material import AddMaterialWindow
            try:
                AddMaterialWindow(self, self.db, material_id=rec[0])
            except Exception as ex:
                messagebox.showerror("Napaka", f"Urejanje ni mogoče: {ex}")
            self.filter_data()
