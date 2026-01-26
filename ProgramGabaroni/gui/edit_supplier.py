import tkinter as tk
from tkinter import ttk, messagebox
from db_manager import DatabaseManager
from utils import unify_string
from gui.theme import apply_theme

class EditSupplierWindow(tk.Toplevel):
    def __init__(self, master, db_manager: DatabaseManager, supplier_id):
        super().__init__(master)
        apply_theme(self)
        self.db = db_manager
        self.supplier_id = supplier_id
        self.title("Uredi dobavitelja")

        # Larger window
        self.geometry("600x400")
        self.minsize(600,400)

        self.bind("<Escape>", lambda e: self.destroy())

        # Polja za ime, naslov, telefon, email, opombe
        tk.Label(self, text="Ime:").grid(row=0, column=0, sticky="e", padx=10, pady=6)
        self.e_name = tk.Entry(self, width=30)
        self.e_name.grid(row=0, column=1, padx=10, pady=6)

        tk.Label(self, text="Naslov:").grid(row=1, column=0, sticky="e", padx=10, pady=6)
        self.e_address = tk.Entry(self, width=30)
        self.e_address.grid(row=1, column=1, padx=10, pady=6)

        tk.Label(self, text="Telefon:").grid(row=2, column=0, sticky="e", padx=10, pady=6)
        self.e_phone = tk.Entry(self, width=30)
        self.e_phone.grid(row=2, column=1, padx=10, pady=6)

        tk.Label(self, text="E-mail:").grid(row=3, column=0, sticky="e", padx=10, pady=6)
        self.e_email = tk.Entry(self, width=30)
        self.e_email.grid(row=3, column=1, padx=10, pady=6)

        tk.Label(self, text="Opombe:").grid(row=4, column=0, sticky="ne", padx=10, pady=6)
        self.txt_notes = tk.Text(self, width=30, height=4)
        self.txt_notes.grid(row=4, column=1, padx=10, pady=6)

        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=14)

        btn_save = ttk.Button(btn_frame, text="Shrani", command=self.save_supplier)
        btn_save.pack(side="left", padx=5)
        btn_save.bind("<Return>", lambda e: btn_save.invoke())

        btn_cancel = ttk.Button(btn_frame, text="Prekliči", style="Secondary.TButton", command=self.destroy)
        btn_cancel.pack(side="left", padx=5)
        btn_cancel.bind("<Return>", lambda e: btn_cancel.invoke())

        self.fill_data()

    def fill_data(self):
        with self.db.connect() as conn:
            c = conn.cursor()
            c.execute("SELECT name, address, phone, email, notes FROM suppliers WHERE id=?", (self.supplier_id,))
            row = c.fetchone()
        if row:
            self.e_name.insert(0, row[0] if row[0] else "")
            self.e_address.insert(0, row[1] if row[1] else "")
            self.e_phone.insert(0, row[2] if row[2] else "")
            self.e_email.insert(0, row[3] if row[3] else "")
            if row[4]:
                self.txt_notes.insert("1.0", row[4])

    def save_supplier(self):
        name = unify_string(self.e_name.get().strip())
        address = unify_string(self.e_address.get().strip())
        phone = unify_string(self.e_phone.get().strip())
        email = unify_string(self.e_email.get().strip())
        notes = unify_string(self.txt_notes.get("1.0", "end").strip())
        if not name:
            messagebox.showerror("Napaka", "Ime je obvezno!")
            return
        with self.db.connect() as conn:
            c = conn.cursor()
            c.execute("""
                UPDATE suppliers
                SET name = ?,
                    address = ?,
                    phone = ?,
                    email = ?,
                    notes = ?
                WHERE id = ?
            """, (name, address, phone, email, notes, self.supplier_id))
            conn.commit()
        messagebox.showinfo("OK", "Dobavitelj posodobljen.")
        self.destroy()
