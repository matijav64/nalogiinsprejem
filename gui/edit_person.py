import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from db_manager import DatabaseManager
from utils import unify_string

class EditPersonWindow(tk.Toplevel):
    def __init__(self, master, db_manager: DatabaseManager, person_id: int):
        super().__init__(master)
        self.db = db_manager
        self.person_id = person_id
        self.title("Uredi prejemca")
        self.geometry("300x150")
        self.bind("<Escape>", lambda e: self.destroy())

        tk.Label(self, text="Ime prejemca:").pack(pady=5)
        self.e_name = tk.Entry(self, width=30)
        self.e_name.pack(pady=5)

        with sqlite3.connect(self.db.db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT name FROM persons WHERE id=?", (person_id,))
            row = c.fetchone()
        if row:
            self.e_name.insert(0, row[0])

        ttk.Button(self, text="Shrani", command=self.save).pack(pady=5)
        ttk.Button(self, text="Briši", command=self.delete).pack(pady=5)

    def save(self):
        name = unify_string(self.e_name.get().strip())
        if name:
            with sqlite3.connect(self.db.db_path) as conn:
                c = conn.cursor()
                c.execute("UPDATE persons SET name=? WHERE id=?", (name, self.person_id))
                conn.commit()
        self.destroy()

    def delete(self):
        if messagebox.askyesno("Brisanje", "Ali res želite izbrisati tega prejemca?"):
            with sqlite3.connect(self.db.db_path) as conn:
                c = conn.cursor()
                c.execute("DELETE FROM persons WHERE id=?", (self.person_id,))
                conn.commit()
            self.destroy()
