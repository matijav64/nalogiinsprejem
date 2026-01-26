import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from utils import unify_string
from gui.theme import apply_theme
from export_utils import export_data_dialog

class ShowStockWindow(tk.Toplevel):
    def __init__(self, master, db_manager):
        super().__init__(master)
        apply_theme(self)
        self.db = db_manager
        self.title("Prikaži stanje zaloge")
        
        # Make the window bigger
        self.geometry("700x500")
        self.minsize(700, 500)
        
        # Apply bigger font
        self.option_add("*Font", ("Segoe UI", 14))

        self.bind("<Escape>", lambda e: self.destroy())

        top_frame = tk.Frame(self)
        top_frame.pack(pady=5, fill="x")

        tk.Label(top_frame, text="Iskanje:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(top_frame, textvariable=self.search_var, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_var.trace_add("write", lambda *args: self.filter_stock())

        btn_filter = ttk.Button(top_frame, text="Filtriraj", command=self.filter_stock)
        btn_filter.pack(side=tk.LEFT, padx=5)
        btn_filter.bind("<Return>", lambda e: btn_filter.invoke())

        btn_export = ttk.Button(top_frame, text="Izvozi", command=self.open_export_dialog)
        btn_export.pack(side=tk.LEFT, padx=5)
        btn_export.bind("<Return>", lambda e: btn_export.invoke())

        self.tree = ttk.Treeview(self, columns=("Surovina", "Količina"), show="headings")
        self.tree.heading("Surovina", text="Surovina")
        self.tree.heading("Količina", text="Količina")
        self.tree.column("Surovina", width=300)
        self.tree.column("Količina", width=100)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.filter_stock()

    def filter_stock(self):
        # Clear existing rows
        for i in self.tree.get_children():
            self.tree.delete(i)

        search_text = unify_string(self.search_var.get()).casefold()
        # Only show items where slediti=1
        query = """
            SELECT mt.category || '->' || mt.subcategory AS surovina,
                   z.kolicina
            FROM zaloge z
            JOIN material_types mt ON z.material_type_id = mt.id
            WHERE mt.slediti = 1
        """
        params = []
        if search_text:
            query += " AND LOWER(mt.category || '->' || mt.subcategory) LIKE ?"
            pattern = f"%{search_text}%"
            params.append(pattern)
        query += " ORDER BY mt.category, mt.subcategory"

        with self.db.connect() as conn:
            c = conn.cursor()
            c.execute(query, params)
            rows = c.fetchall()

        for r in rows:
            self.tree.insert("", "end", values=r)

    def open_export_dialog(self):
        data = [list(self.tree.item(child)["values"]) for child in self.tree.get_children()]
        if not data:
            messagebox.showwarning("Opozorilo", "Ni podatkov za izvoz!")
            return
        headers = ["surovina", "kolicina"]
        export_data_dialog(headers, data, "zaloge", "Stock")
