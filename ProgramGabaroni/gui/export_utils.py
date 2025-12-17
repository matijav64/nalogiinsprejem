import csv
import pandas as pd
import xml.etree.ElementTree as ET
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from tkinter import filedialog, messagebox, Toplevel, BooleanVar, Checkbutton, Radiobutton, Frame, ttk

def escape_sql_value(v):
    if v is None:
        return "NULL"
    return "'" + str(v).replace("'", "''") + "'"

def export_to_pdf(headers, data, filename):
    doc = SimpleDocTemplate(filename, pagesize=letter)
    table_data = [headers] + data
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 12),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ]))
    doc.build([table])

def export_to_xml(headers, data, root_name, filename):
    root = ET.Element(root_name)
    # Carefully ensuring indentation:
    for row in data:
        rec = ET.SubElement(root, "record")
        for h, val in zip(headers, row):
            child = ET.SubElement(rec, h.replace(" ", "_"))
            child.text = str(val) if val is not None else ""
    tree = ET.ElementTree(root)
    tree.write(filename, encoding="utf-8", xml_declaration=True)

def export_to_sql(headers, data, table_name, filename):
    with open(filename, "w", encoding="utf-8") as f:
        for row in data:
            vals = [escape_sql_value(v) for v in row]
            sql = f"INSERT INTO {table_name} ({', '.join(headers)}) VALUES ({', '.join(vals)});\n"
            f.write(sql)

def export_to_csv(headers, data, filename):
    df = pd.DataFrame(data, columns=headers)
    df.to_csv(filename, index=False)

def export_data_dialog(headers, data, table_name, root_name):
    def do_export():
        selected = [h for h, var in zip(headers, vars_list) if var.get()]
        if not selected:
            messagebox.showwarning("Opozorilo", "Izberite vsaj en stolpec!")
            return
        idxs = [i for i, var in enumerate(vars_list) if var.get()]
        new_data = [[row[i] for i in idxs] for row in data]
        new_headers = [headers[i] for i in idxs]
        fmt = export_fmt.get()
        fname = filedialog.asksaveasfilename(
            defaultextension=f".{fmt}",
            filetypes=[(f"{fmt.upper()} files", f"*.{fmt}")]
        )
        if not fname:
            return
        if fmt == "pdf":
            export_to_pdf(new_headers, new_data, fname)
        elif fmt == "xml":
            export_to_xml(new_headers, new_data, root_name, fname)
        elif fmt == "sql":
            export_to_sql(new_headers, new_data, table_name, fname)
        elif fmt == "csv":
            export_to_csv(new_headers, new_data, fname)
        messagebox.showinfo("Izvoz", f"Izvo≈æeno v {fmt.upper()}: {fname}")
        top.destroy()

    top = Toplevel()
    top.title("Izberi stolpce za izvoz")
    top.geometry("300x500")
    top.bind("<Escape>", lambda e: top.destroy())

    import tkinter as tk
    from tkinter import ttk

    tk.Label(top, text="Izberi stolpce:").pack(pady=5)
    vars_list = []
    for h in headers:
        var = BooleanVar(value=True)
        chk = Checkbutton(top, text=h, variable=var)
        chk.pack(anchor="w")
        vars_list.append(var)

    tk.Label(top, text="Izberi format:").pack(pady=5)
    export_fmt = tk.StringVar(value="pdf")
    fmt_frame = Frame(top)
    fmt_frame.pack(pady=5)
    for fval in ["pdf", "xml", "sql", "csv"]:
        rb = Radiobutton(fmt_frame, text=fval.upper(), variable=export_fmt, value=fval)
        rb.pack(side="left", padx=2)

    ttk.Button(top, text="Izvozi", command=do_export).pack(pady=20)
