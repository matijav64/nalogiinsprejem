import tkinter as tk
from tkinter import ttk, messagebox
from db_manager import DatabaseManager
from utils import unify_string
from gui.theme import apply_theme

class EditFullMaterialWindow(tk.Toplevel):
    def __init__(self, master, db_manager: DatabaseManager):
        super().__init__(master)
        apply_theme(self)
        self.db = db_manager
        self.title("Edit Full Material")
        self.geometry("600x400")
        self.bind("<Escape>", lambda e: self.destroy())

        tk.Label(self, text="ID materiala za urejanje:").pack(pady=5)
        self.e_id = tk.Entry(self, width=10)
        self.e_id.pack(pady=5)
        ttk.Button(self, text="Naloži material", command=self.load_material).pack(pady=5)

        tk.Label(self, text="Novi podatki:").pack(pady=5)
        self.e_newinfo = tk.Entry(self, width=50)
        self.e_newinfo.pack(pady=5)
        ttk.Button(self, text="Shrani spremembe", command=self.save_changes).pack(pady=5)

    def load_material(self):
        mat_id_str = unify_string(self.e_id.get().strip())
        if not mat_id_str.isdigit():
            messagebox.showerror("Napaka", "Vnesite veljaven (številčni) ID.")
            return
        mat_id = int(mat_id_str)
        with self.db.connect() as conn:
            c = conn.cursor()
            c.execute("SELECT generirana_koda FROM prejeti_materiali WHERE id=?", (mat_id,))
            row = c.fetchone()
            if not row:
                messagebox.showerror("Napaka", f"Material z ID={mat_id} ne obstaja.")
                return
            self.e_newinfo.delete(0, tk.END)
            self.e_newinfo.insert(0, row[0])

    def save_changes(self):
        mat_id_str = unify_string(self.e_id.get().strip())
        if not mat_id_str.isdigit():
            messagebox.showerror("Napaka", "Vnesite veljaven (številčni) ID.")
            return
        mat_id = int(mat_id_str)

        new_val = unify_string(self.e_newinfo.get().strip())
        if not new_val:
            messagebox.showerror("Napaka", "Nov vnos je prazen.")
            return

        with self.db.connect() as conn:
            c = conn.cursor()
            c.execute("UPDATE prejeti_materiali SET generirana_koda=? WHERE id=?", (new_val, mat_id))
            conn.commit()

        messagebox.showinfo("OK", f"Material ID={mat_id} posodobljen.")
        self.destroy()
