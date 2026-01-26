import tkinter as tk
from tkinter import ttk, messagebox
from db_manager import DatabaseManager
from utils import unify_string
from gui.theme import apply_theme

class EditSingleRawMaterialWindow(tk.Toplevel):
    def __init__(self, master, db_manager: DatabaseManager, record):
        super().__init__(master)
        apply_theme(self)
        self.db = db_manager
        self.title("Uredi surovino")

        # Larger window
        self.geometry("600x400")
        self.minsize(600, 400)
        self.bind("<Escape>", lambda e: self.destroy())

        # record => (id, category, subcategory, code, slediti)
        self.rid, self.cat, self.sub, self.code, self.sled = record
        
        tk.Label(self, text="Kategorija:").grid(row=0, column=0, sticky="e", padx=10, pady=6)
        self.e_cat = tk.Entry(self, width=20)
        self.e_cat.grid(row=0, column=1, padx=10, pady=6)
        self.e_cat.insert(0, self.cat)
        
        tk.Label(self, text="Podkategorija:").grid(row=1, column=0, sticky="e", padx=10, pady=6)
        self.e_sub = tk.Entry(self, width=20)
        self.e_sub.grid(row=1, column=1, padx=10, pady=6)
        self.e_sub.insert(0, self.sub)
        
        tk.Label(self, text="Koda:").grid(row=2, column=0, sticky="e", padx=10, pady=6)
        self.e_code = tk.Entry(self, width=10)
        self.e_code.grid(row=2, column=1, padx=10, pady=6)
        self.e_code.insert(0, self.code)
        
        self.var_sled = tk.IntVar(value=self.sled)
        tk.Checkbutton(self, text="Slediti zalogi?", variable=self.var_sled).grid(row=3, column=0, columnspan=2, pady=8)
        
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=14)
        
        btn_save = ttk.Button(btn_frame, text="Shrani", command=self.save_mat)
        btn_save.pack(side="left", padx=5)
        btn_cancel = ttk.Button(btn_frame, text="Prekliči", style="Secondary.TButton", command=self.destroy)
        btn_cancel.pack(side="left", padx=5)

    def save_mat(self):
        new_cat = unify_string(self.e_cat.get().strip())
        new_sub = unify_string(self.e_sub.get().strip())
        new_code = unify_string(self.e_code.get().strip())
        new_sled = self.var_sled.get()
        if not new_cat or not new_sub or not new_code:
            messagebox.showerror("Napaka", "Prazna polja!")
            return
        with self.db.connect() as conn:
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
