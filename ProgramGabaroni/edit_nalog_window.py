import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from db_manager import DatabaseManager
from utils import unify_string

class EditNalogWindow(tk.Toplevel):
    def __init__(self, master, db_manager: DatabaseManager):
        super().__init__(master)
        self.db = db_manager
        self.title("Edit Nalog Window")
        self.geometry("600x400")
        self.bind("<Escape>", lambda e: self.destroy())

        tk.Label(self, text="ID naloga:").pack(pady=5)
        self.e_id = tk.Entry(self)
        self.e_id.pack(pady=5)
        ttk.Button(self, text="Naloži", command=self.load_nalog).pack(pady=5)

        self.e_info = tk.Entry(self, width=50)
        self.e_info.pack(pady=5)

        ttk.Button(self, text="Shrani", command=self.save_nalog).pack(pady=5)

    def load_nalog(self):
        val_str = unify_string(self.e_id.get().strip())
        if not val_str.isdigit():
            messagebox.showerror("Napaka", "ID mora biti število.")
            return
        nalog_id = int(val_str)
        with sqlite3.connect(self.db.db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT izbrani_lot FROM delovni_nalog WHERE id=?", (nalog_id,))
            row = c.fetchone()
            if row:
                self.e_info.delete(0, tk.END)
                self.e_info.insert(0, row[0])
            else:
                messagebox.showerror("Napaka", f"Nalog {nalog_id} ne obstaja.")

    def save_nalog(self):
        val_str = unify_string(self.e_id.get().strip())
        if not val_str.isdigit():
            messagebox.showerror("Napaka", "ID mora biti število.")
            return
        nalog_id = int(val_str)
        new_val = unify_string(self.e_info.get().strip())
        if not new_val:
            messagebox.showerror("Napaka", "Prazna vrednost.")
            return

        with sqlite3.connect(self.db.db_path) as conn:
            c = conn.cursor()
            c.execute("UPDATE delovni_nalog SET izbrani_lot=? WHERE id=?", (new_val, nalog_id))
            conn.commit()
        messagebox.showinfo("OK", f"Nalog {nalog_id} posodobljen.")
        self.destroy()
