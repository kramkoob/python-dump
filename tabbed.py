#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title("Tkinter Tabbed Window")
root.geometry("400x300")

# Create the Notebook (tab control)
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both")

# Create frames for each tab
tab1 = ttk.Frame(notebook)
tab2 = ttk.Frame(notebook)

# Add frames to the notebook with labels
notebook.add(tab1, text="General Settings")
notebook.add(tab2, text="Advanced")

# Add content to the first tab
label1 = ttk.Label(tab1, text="This is the main settings page.")
label1.pack(padx=10, pady=10)

# Add content to the second tab
label2 = ttk.Label(tab2, text="Advanced options go here.")
label2.pack(padx=10, pady=10)

root.mainloop()