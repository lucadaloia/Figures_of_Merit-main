# GUI to select PDFs to be parsed
# function will return a list of the paths to the selected files

import tkinter as tk
from tkinter import filedialog

def select_pdfs():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_paths = filedialog.askopenfilenames(
        title="Select PDF files",
        filetypes=[("PDF files", "*.pdf")],
    )
    return list(file_paths)

    