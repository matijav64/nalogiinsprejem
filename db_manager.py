import sqlite3
from typing import List, Tuple

class DatabaseManager:
    def __init__(self, db_path="sledenje.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            # Suppliers table with extra columns
            c.execute('''CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                address TEXT,
                phone TEXT,
                email TEXT,
                notes TEXT
            )''')
            # Carriers table with extra columns
            c.execute('''CREATE TABLE IF NOT EXISTS carriers (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                address TEXT,
                phone TEXT,
                email TEXT,
                notes TEXT
            )''')
            # Persons table (unchanged)
            c.execute('''CREATE TABLE IF NOT EXISTS persons (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL
            )''')
            # Material types
            c.execute('''CREATE TABLE IF NOT EXISTS material_types (
                id INTEGER PRIMARY KEY,
                category TEXT NOT NULL,
                subcategory TEXT NOT NULL,
                code TEXT NOT NULL,
                slediti INTEGER NOT NULL DEFAULT 1,
                UNIQUE(category, subcategory)
            )''')
            # Prejeti materiali (received materials)
            c.execute('''CREATE TABLE IF NOT EXISTS prejeti_materiali (
                id INTEGER PRIMARY KEY,
                datum_prejema TEXT NOT NULL,
                supplier_id INTEGER NOT NULL,
                carrier_id INTEGER,
                rok_uporabe TEXT,
                embalaza_ok TEXT,
                skladisce_ok TEXT,
                reklamacije TEXT,
                person_id INTEGER NOT NULL,
                material_type_id INTEGER NOT NULL,
                generirana_koda TEXT,
                kolicina REAL
            )''')
            # Delovni nalog (work orders) – fixed columns only for core info
            c.execute('''CREATE TABLE IF NOT EXISTS delovni_nalog (
                id INTEGER PRIMARY KEY,
                datum_dela TEXT NOT NULL,
                lot_prejsnji_id INTEGER,
                izbrani_lot TEXT,
                nova_oblika TEXT,
                kolicina REAL,
                nov_lot TEXT
            )''')
            # Dynamic ingredients for work orders
            c.execute('''CREATE TABLE IF NOT EXISTS delovni_nalog_sestavine (
                id INTEGER PRIMARY KEY,
                delovni_nalog_id INTEGER NOT NULL,
                sestavina TEXT,
                kolicina REAL,
                FOREIGN KEY(delovni_nalog_id) REFERENCES delovni_nalog(id)
            )''')
            # Zaloge (stock)
            c.execute('''CREATE TABLE IF NOT EXISTS zaloge (
                id INTEGER PRIMARY KEY,
                material_type_id INTEGER NOT NULL,
                kolicina REAL NOT NULL DEFAULT 0
            )''')
            conn.commit()

            # Insert default entries if tables are empty

            # Material types defaults
            c.execute("SELECT COUNT(*) FROM material_types")
            if c.fetchone()[0] == 0:
                defaults = [
                    ("Moka", "Durum", "IT1", 1),
                    ("Moka", "Pirina", "VN3", 1),
                    ("Moka", "Čičerika", "PL3", 1),
                    ("Moka", "Rdeča leča", "PL2", 1),
                    ("Moka", "Zeleni Grah", "PL5", 1),
                    ("Moka", "Črni Fižol", "PL4", 1),
                    ("Moka", "Ajda", "Č1", 1),
                    ("Moka", "Kamut", "VN6", 1),
                    ("Moka", "Psyllium", "PS", 1),
                    ("Moka", "Bučna", "BU", 1),
                    ("Moka", "Lanena", "LA", 1),
                    ("Sok", "rdeče pese", "RP", 1),
                    ("Zelenjava", "blitva", "BL", 1),
                    ("Dodatki", "Kurkuma", "KUR", 1),
                    ("Dodatki", "aktivno oglje", "AKO", 1),
                    ("Dodatki", "kakav", "KKV", 1)
                ]
                for cat, sub, code, sled in defaults:
                    c.execute("INSERT INTO material_types (category, subcategory, code, slediti) VALUES (?,?,?,?)",
                              (cat, sub, code, sled))
            # Suppliers defaults
            c.execute("SELECT COUNT(*) FROM suppliers")
            if c.fetchone()[0] == 0:
                for s in ["Molino Grassi", "Vila Natura", "Prema d.o.o."]:
                    c.execute("INSERT INTO suppliers (name) VALUES (?)", (s,))
            # Carriers defaults
            c.execute("SELECT COUNT(*) FROM carriers")
            if c.fetchone()[0] == 0:
                for cval in ["Pošta Slovenije", "Rhenus Logistika"]:
                    c.execute("INSERT INTO carriers (name) VALUES (?)", (cval,))
            # Persons defaults
            c.execute("SELECT COUNT(*) FROM persons")
            if c.fetchone()[0] == 0:
                for p in ["Matija", "Nastja", "Sabina"]:
                    c.execute("INSERT INTO persons (name) VALUES (?)", (p,))
            conn.commit()

    def get_subcategories(self, cat: str) -> List[Tuple[str, str]]:
        with sqlite3.connect(self.db_path) as conn:
            cu = conn.cursor()
            cu.execute("SELECT subcategory, code FROM material_types WHERE category=? ORDER BY subcategory", (cat,))
            return cu.fetchall()

    def get_or_create_material_type(self, cat: str, subc: str, code: str) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cu = conn.cursor()
            cu.execute("SELECT id FROM material_types WHERE category=? AND subcategory=?", (cat, subc))
            row = cu.fetchone()
            if row:
                return row[0]
            cu.execute("INSERT INTO material_types (category, subcategory, code, slediti) VALUES (?,?,?,1)",
                       (cat, subc, code))
            conn.commit()
            return cu.lastrowid

    def update_stock(self, material_type_id: int, qty_diff: float):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT slediti FROM material_types WHERE id=?", (material_type_id,))
            row = c.fetchone()
            if row and row[0] == 0:
                return
            c.execute("SELECT kolicina FROM zaloge WHERE material_type_id=?", (material_type_id,))
            r2 = c.fetchone()
            if r2:
                new_qty = r2[0] + qty_diff
                c.execute("UPDATE zaloge SET kolicina=? WHERE material_type_id=?", (new_qty, material_type_id))
            else:
                c.execute("INSERT INTO zaloge (material_type_id, kolicina) VALUES (?,?)", (material_type_id, qty_diff))
            conn.commit()

    def set_stock(self, material_type_id: int, new_qty: float):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT id FROM zaloge WHERE material_type_id=?", (material_type_id,))
            row = c.fetchone()
            if row:
                c.execute("UPDATE zaloge SET kolicina=? WHERE material_type_id=?", (new_qty, material_type_id))
            else:
                c.execute("INSERT INTO zaloge (material_type_id, kolicina) VALUES (?,?)", (material_type_id, new_qty))
            conn.commit()
