import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from db_manager import DatabaseManager
from utils import unify_string

class EditSingleRawMaterialWindow(tk.Toplevel):
    def __init__(self, master, db_manager: DatabaseManager, record):
        super().__init__(master)
        self.db = db_manager
        self.title("Uredi surovino")

        # Larger window
        self.geometry("600x400")
        self.minsize(600, 400)
        self.option_add("*Font", ("Segoe UI", 14))

        self.bind("<Escape>", lambda e: self.destroy())

        # record => (id, category, subcategory, code, slediti)
        self.rid, self.cat, self.sub, self.code, self.sled = record
        
        tk.Label(self, text="Kategorija:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.e_cat = tk.Entry(self, width=20)
        self.e_cat.grid(row=0, column=1, padx=5, pady=5)
        self.e_cat.insert(0, self.cat)
        
        tk.Label(self, text="Podkategorija:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.e_sub = tk.Entry(self, width=20)
        self.e_sub.grid(row=1, column=1, padx=5, pady=5)
        self.e_sub.insert(0, self.sub)
        
        tk.Label(self, text="Koda:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.e_code = tk.Entry(self, width=10)
        self.e_code.grid(row=2, column=1, padx=5, pady=5)
        self.e_code.insert(0, self.code)
        
        self.var_sled = tk.IntVar(value=self.sled)
        tk.Checkbutton(self, text="Slediti zalogi?", variable=self.var_sled).grid(row=3, column=0, columnspan=2, pady=5)
        
        btn_frame = tk.Frame(self)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        btn_save = ttk.Button(btn_frame, text="Shrani", command=self.save_mat)
        btn_save.pack(side="left", padx=5)
        btn_cancel = ttk.Button(btn_frame, text="Prekliči", command=self.destroy)
        btn_cancel.pack(side="left", padx=5)

    def save_mat(self):
        new_cat = unify_string(self.e_cat.get().strip())
        new_sub = unify_string(self.e_sub.get().strip())
        new_code = unify_string(self.e_code.get().strip())
        new_sled = self.var_sled.get()
        if not new_cat or not new_sub or not new_code:
            messagebox.showerror("Napaka", "Prazna polja!")
            return
        with sqlite3.connect(self.db.db_path) as conn:
            c = conn.cursor()
            c.execute("""
                UPDATE material_types
                SET category = ?,
                    subcategory = ?,
                    code = ?,
                    slediti = ?
                WHERE id = ?
            """, (new_cat, new_sub, new_code, new_sled, self.rid))
            conn.commit()
        messagebox.showinfo("OK", "Posodobljeno.")
        self.destroy()
