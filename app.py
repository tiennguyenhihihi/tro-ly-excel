import tkinter as tk
from tkinter import filedialog, messagebox
import pdfplumber
import pandas as pd

def process_pdf():
    pdf_file = filedialog.askopenfilename(
        title="Chọn file PDF",
        filetypes=[("PDF files", "*.pdf")]
    )

    if not pdf_file:
        return

    serials = []

    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()

            for table in tables:
                if not table:
                    continue

                headers = [str(x).strip() if x else "" for x in table[0]]

                if "SN" not in [h.upper() for h in headers]:
                    continue

                sn_col = [h.upper() for h in headers].index("SN")

                for row in table[1:]:
                    if len(row) > sn_col and row[sn_col]:
                        serials.append(str(row[sn_col]).strip())

    output_file = "SN_Output.xlsx"

    pd.DataFrame({"SN": serials}).to_excel(
        output_file,
        index=False
    )

    messagebox.showinfo(
        "Hoàn thành",
        f"Đã xuất {len(serials)} serial vào\n{output_file}"
    )

root = tk.Tk()
root.title("AI Serial Extractor")

btn = tk.Button(
    root,
    text="Chọn PDF và xuất Serial",
    command=process_pdf,
    width=30,
    height=2
)

btn.pack(padx=20, pady=20)

root.mainloop()