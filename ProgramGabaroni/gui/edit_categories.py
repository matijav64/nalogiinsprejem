import tkinter as tk
from tkinter import ttk
from db_manager import DatabaseManager
from gui.edit_categories_helper import (
    EditRawMaterialsWindow,
    EditSuppliersWindow,
    EditCarriersWindow,
    EditPersonsWindow,
    EditShapesWindow,
)
from gui.theme import apply_theme

class EditCategoriesWindow(tk.Toplevel):
    def __init__(self, master, db_manager: DatabaseManager):
        super().__init__(master)
        apply_theme(self)
        self.db = db_manager
        self.title("Uredi kategorije")

        # Larger window
        self.geometry("600x400")
        self.minsize(600, 400)

        self.bind("<Escape>", lambda e: self.destroy())

        ttk.Button(self, text="Uredi surovine", command=self.edit_surovine).pack(pady=10, padx=20, fill="x")
        ttk.Button(self, text="Uredi dobavitelje", command=self.edit_suppliers).pack(pady=10, padx=20, fill="x")
        ttk.Button(self, text="Uredi prevoznike", command=self.edit_carriers).pack(pady=10, padx=20, fill="x")
        ttk.Button(self, text="Uredi prejemce", command=self.edit_persons).pack(pady=10, padx=20, fill="x")
        ttk.Button(self, text="Uredi oblike", command=self.edit_shapes).pack(pady=10, padx=20, fill="x")

    def edit_surovine(self):
        EditRawMaterialsWindow(self, self.db)

    def edit_suppliers(self):
        EditSuppliersWindow(self, self.db)

    def edit_carriers(self):
        EditCarriersWindow(self, self.db)

    def edit_persons(self):
        EditPersonsWindow(self, self.db)

    def edit_shapes(self):
        EditShapesWindow(self, self.db)
