import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from utils import unify_string, format_ymd_to_ddmmYYYY
from export_utils import export_data_dialog
from gui.theme import apply_theme

class ShowNalogiWindow(tk.Toplevel):
    def __init__(self, master, db_manager):
        super().__init__(master)
        apply_theme(self)
        self.db = db_manager
        self.title("Izpiši delovne naloge")
        self.geometry("1220x700")
        self.bind("<Escape>", lambda e: self.destroy())
        
        top_frame = tk.Frame(self)
        top_frame.pack(pady=5, fill="x")
        tk.Label(top_frame, text="Iskanje:").grid(row=0, column=0, padx=3, pady=3, sticky="e")
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(top_frame, textvariable=self.search_var, width=30)
        self.search_entry.grid(row=0, column=1, padx=3, pady=3)
        self.search_var.trace_add("write", lambda *args: self.reset_and_filter())
        
        btn_filter = ttk.Button(top_frame, text="Filtriraj", command=self.reset_and_filter)
        btn_filter.grid(row=0, column=2, padx=5, pady=3)
        btn_filter.bind("<Return>", lambda e: btn_filter.invoke())

        self.prev_button = ttk.Button(top_frame, text="Nazaj", command=self.show_prev_page)
        self.prev_button.grid(row=0, column=3, padx=5, pady=3)
        self.prev_button.bind("<Return>", lambda e: self.prev_button.invoke())

        self.next_button = ttk.Button(top_frame, text="Več", command=self.show_next_page)
        self.next_button.grid(row=0, column=4, padx=5, pady=3)
        self.next_button.bind("<Return>", lambda e: self.next_button.invoke())
        
        btn_export = ttk.Button(top_frame, text="Izvozi", command=self.open_export_dialog)
        btn_export.grid(row=0, column=5, padx=5, pady=3)
        btn_export.bind("<Return>", lambda e: btn_export.invoke())

        self.page_size = 6
        self.offset = 0
        self.total_rows = 0
        
        cols = ("ID", "Datum dela", "Izbrani LOT", "Oblika", "Količina", "Nov LOT", "Sestavine")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=110)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.on_double_click)
        self.filter_data()
        self.update_idletasks()
        self.geometry(f"{self.winfo_reqwidth()}x{self.winfo_reqheight()}")

    def reset_and_filter(self, event=None):
        self.offset = 0
        self.filter_data()

    def show_next_page(self):
        if self.offset + self.page_size < self.total_rows:
            self.offset += self.page_size
            self.filter_data()

    def show_prev_page(self):
        if self.offset >= self.page_size:
            self.offset -= self.page_size
            self.filter_data()

    def filter_data(self, event=None):
        for i in self.tree.get_children():
            self.tree.delete(i)
        search_text = unify_string(self.search_var.get()).casefold()
        sestavine_expr = """
            IFNULL(
                (SELECT GROUP_CONCAT(sestavina || ' (qty: ' || kolicina || ')', ', ')
                 FROM delovni_nalog_sestavine
                 WHERE delovni_nalog_id = d.id
                ),
                ''
            )
        """
        query = f"""
            SELECT d.id,
                   FORMAT_DATE(d.datum_dela) AS datum,
                   d.izbrani_lot,
                   d.nova_oblika,
                   d.kolicina,
                   d.nov_lot,
                   {sestavine_expr} AS sestavine
            FROM delovni_nalog d
        """
        where_clauses = []
        params = []
        if search_text:
            where_clauses.append(
                f"""(
                    LOWER(d.izbrani_lot) LIKE ? OR
                    LOWER(d.nova_oblika) LIKE ? OR
                    LOWER(FORMAT_DATE(d.datum_dela)) LIKE ? OR
                    LOWER(d.nov_lot) LIKE ? OR
                    LOWER({sestavine_expr}) LIKE ?
                )"""
            )
            pattern = f"%{search_text}%"
            params.extend([pattern] * 5)
        where_sql = ""
        if where_clauses:
            where_sql = " WHERE " + " AND ".join(where_clauses)
        query += f"{where_sql} ORDER BY d.id DESC LIMIT ? OFFSET ?"
        with self.db.connect() as conn:
            conn.create_function("FORMAT_DATE", 1, format_ymd_to_ddmmYYYY)
            conn.create_function("LOWER", 1, lambda s: s.lower() if s else "")
            c = conn.cursor()
            count_query = f"SELECT COUNT(*) FROM delovni_nalog d{where_sql}"
            c.execute(count_query, params)
            self.total_rows = c.fetchone()[0] or 0
            c.execute(query, params + [self.page_size, self.offset])
            rows = c.fetchall()
        for row in rows:
            self.tree.insert("", "end", values=row)

        self.prev_button.configure(state="normal" if self.offset >= self.page_size else "disabled")
        self.next_button.configure(
            state="normal" if self.offset + self.page_size < self.total_rows else "disabled"
        )

    def open_export_dialog(self):
        data = [list(self.tree.item(child)["values"]) for child in self.tree.get_children()]
        if not data:
            messagebox.showwarning("Opozorilo", "Ni podatkov za izvoz!")
            return
        headers = ["ID", "datum_dela", "izbrani_lot", "nova_oblika", "kolicina", "nov_lot", "sestavine"]
        export_data_dialog(headers, data, "delovni_nalog", "WorkOrders")

    def on_double_click(self, event):
        item = self.tree.focus()
        if item:
            rec = self.tree.item(item)["values"]
            from gui.add_nalog import AddNalogWindow
            try:
                AddNalogWindow(self, self.db, nalog_id=rec[0])
            except Exception as ex:
                messagebox.showerror("Napaka", f"Urejanje ni mogoče: {ex}")
            self.filter_data()
