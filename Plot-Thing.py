#!/usr/bin/env python3
# Manipulating matplotlib in a graphical interface
# by Thomas Dodds
# 2/22/2026

import matplotlib.pyplot as plt
import matplotlib.transforms as pltf
import numpy as np
import io
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

# Example data
x = np.linspace(0, 10, 100)
y = np.sin(x)
y2 = np.cos(x)

def value_changed(*args):
    plt.figure(figsize=(width_in, height_in))
    plt.plot(x, y, color='b', label="sin(x)")
    plt.plot(x, y2, color='r', label="cos(x)")
    plt.title("Sine Wave")
    plt.xlabel("X-axis")
    plt.ylabel("Y-axis")
    plt.legend()
    
    plot_cursor.set(int(float(plot_cursor.get())))
    
    closest_x = x[int(plot_cursor.get())]
    closest_y = y[int(plot_cursor.get())]
    closest_y2 = y2[int(plot_cursor.get())]

    plt.axhline(y=closest_y, color='b', label='Cursor')
    plt.axhline(y=closest_y2, color='r', label='Cursor')
    plt.axvline(x=closest_x, color='k', label='Cursor')
    
    plot_cursor_value.config(text=f"Cursor (I:{int(plot_cursor.get())})\nX:{closest_x}\nY1:{closest_y}\nY2:{closest_y2}")
    
    plt.xlim(xlim_min, xlim_max)
    plt.ylim(ylim_min, ylim_max)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches=pltf.Bbox([[-.2, -.2], [width_in + .1, height_in + .1]]), pad_inches=0)
    plt.close()
    buf.seek(0)
    
    new_img = ImageTk.PhotoImage(Image.open(buf))
    label.config(image=new_img)
    label.image = new_img # Keep a reference to avoid garbage collection

def sbox_scale(*args):
    global xlim_min, xlim_max, ylim_min, ylim_max
    
    xlim_min = float(plot_xcenter.get()) - float(plot_xscale.get()) / 2
    xlim_max = float(plot_xcenter.get()) + float(plot_xscale.get()) / 2
    ylim_min = float(plot_ycenter.get()) - float(plot_yscale.get()) / 2
    ylim_max = float(plot_ycenter.get()) + float(plot_yscale.get()) / 2
    
    plot_xlim_min.set(xlim_min)
    plot_xlim_max.set(xlim_max)
    plot_ylim_min.set(ylim_min)
    plot_ylim_max.set(ylim_max)
    
    value_changed()
    
def sbox_lim(*args):
    global xlim_min, xlim_max, ylim_min, ylim_max

    xlim_min = float(plot_xlim_min.get())
    xlim_max = float(plot_xlim_max.get())
    ylim_min = float(plot_ylim_min.get())
    ylim_max = float(plot_ylim_max.get())
    
    xcenter = (xlim_min + xlim_max) / 2
    xscale = (xlim_max - xlim_min)
    ycenter = (ylim_min + ylim_max) / 2
    yscale = (ylim_max - ylim_min)
    
    plot_xcenter.set(xcenter)
    plot_xscale.set(xscale)
    plot_ycenter.set(ycenter)
    plot_yscale.set(yscale)
    
    value_changed()

root = tk.Tk()
root.geometry("800x600")
root.title("Plot-Thing")

width_px = 600
height_px = 400

dpi = plt.rcParams['figure.dpi']
width_in = width_px / dpi
height_in = height_px / dpi

xlim_min = 0
xlim_max = 10
ylim_min = -1
ylim_max = 1

root.rowconfigure(0, weight=9)
for i in range(1,5,1):
    root.rowconfigure(i, weight=1)
for i in range(5):
    root.columnconfigure(i, weight=1)

plt.figure(figsize=(width_in, height_in))
plt.plot(x, y, label="sin(x)")
plt.title("Sine Wave")
plt.xlabel("X-axis")
plt.ylabel("Y-axis")
plt.legend()

plt.xlim(xlim_min, xlim_max)
plt.ylim(ylim_min, ylim_max)

buf = io.BytesIO()
plt.savefig(buf, format='png', bbox_inches=pltf.Bbox([[-.2, -.2], [width_in + .1, height_in + .1]]), pad_inches=0)
plt.close()
buf.seek(0)

first_img = ImageTk.PhotoImage(Image.open(buf))
label = tk.Label(root, image=first_img)
label.image = first_img
label.grid(row=0, column=1, columnspan=4)

#%% Center and scale spinboxes

plot_xcenter_label = tk.Label(root, text="X center")
plot_xcenter_label.grid(row=1, column=1)

plot_xcenter = tk.StringVar(value=5)
plot_xcenter_sbox = ttk.Spinbox(
    root,
    from_=0,
    to=10,
    textvariable=plot_xcenter,
    command=sbox_scale
)
plot_xcenter_sbox.bind("<Return>", sbox_scale)
plot_xcenter_sbox.grid(row=1, column=2)

plot_xscale_label = tk.Label(root, text="X scale")
plot_xscale_label.grid(row=2, column=1)

plot_xscale = tk.StringVar(value=10)
plot_xscale_sbox = ttk.Spinbox(
    root,
    from_=1,
    to=10,
    values=(10, 8, 5, 3, 2, 1, 0.5),
    textvariable=plot_xscale,
    command=sbox_scale
)
plot_xscale_sbox.bind("<Return>", sbox_scale)
plot_xscale_sbox.grid(row=2, column=2)

plot_ycenter_label = tk.Label(root, text="Y center")
plot_ycenter_label.grid(row=3, column=1)

plot_ycenter = tk.StringVar(value=0)
plot_ycenter_sbox = ttk.Spinbox(
    root,
    from_=-1,
    to=1,
    values=(-1, -.8, -.6, -.4, -.2, 0, .2, .4, .6, .8, 1),
    textvariable=plot_ycenter,
    command=sbox_scale
)
plot_ycenter_sbox.bind("<Return>", sbox_scale)
plot_ycenter_sbox.grid(row=3, column=2)

plot_yscale_label = tk.Label(root, text="Y scale")
plot_yscale_label.grid(row=4, column=1)

plot_yscale = tk.StringVar(value=2)
plot_yscale_sbox = ttk.Spinbox(
    root,
    from_=0.1,
    to=10,
    values=(0.1, 0.25, 0.34, 0.5, 1, 2, 3, 5),
    textvariable=plot_yscale,
    command=sbox_scale
)
plot_yscale_sbox.bind("<Return>", sbox_scale)
plot_yscale_sbox.grid(row=4, column=2)

#%% Limit spinboxes

plot_xlim_min_label = tk.Label(root, text="X minimum")
plot_xlim_min_label.grid(row=1, column=3)

plot_xlim_min = tk.StringVar(value=0)
plot_xlim_min_sbox = ttk.Spinbox(
    root,
    from_=0,
    to=9,
    textvariable=plot_xlim_min,
    command=sbox_lim
)
plot_xlim_min_sbox.bind("<Return>", sbox_lim)
plot_xlim_min_sbox.grid(row=1, column=4)

plot_xlim_max_label = tk.Label(root, text="X maximum")
plot_xlim_max_label.grid(row=2, column=3)

plot_xlim_max = tk.StringVar(value=10)
plot_xlim_max_sbox = ttk.Spinbox(
    root,
    from_=1,
    to=10,
    textvariable=plot_xlim_max,
    command=sbox_lim
)
plot_xlim_max_sbox.bind("<Return>", sbox_lim)
plot_xlim_max_sbox.grid(row=2, column=4)

plot_ylim_min_label = tk.Label(root, text="Y minimum")
plot_ylim_min_label.grid(row=3, column=3)

plot_ylim_min = tk.StringVar(value=-1)
plot_ylim_min_sbox = ttk.Spinbox(
    root,
    from_=-1,
    to=1,
    textvariable=plot_ylim_min,
    command=sbox_lim
)
plot_ylim_min_sbox.bind("<Return>", sbox_lim)
plot_ylim_min_sbox.grid(row=3, column=4)

plot_ylim_max_label = tk.Label(root, text="Y maximum")
plot_ylim_max_label.grid(row=4, column=3)

plot_ylim_max = tk.StringVar(value=1)
plot_ylim_max_sbox = ttk.Spinbox(
    root,
    from_=-1,
    to=1,
    textvariable=plot_ylim_max,
    command=sbox_lim
)
plot_ylim_max_sbox.bind("<Return>", sbox_lim)
plot_ylim_max_sbox.grid(row=4, column=4)

#%% Cursor
plot_cursor = tk.StringVar(value=0)
plot_cursor_sbox = ttk.Spinbox(
    root,
    values=list(range(len(list(x)))),
    textvariable=plot_cursor,
    wrap=True,
    command=value_changed
)
plot_cursor_sbox.bind("<Return>", value_changed)
plot_cursor_sbox.grid(row=1, column=0)

plot_cursor_value = tk.Label(root, text="Cursor:\n[not updated]")
plot_cursor_value.grid(row=2, column=0, rowspan=3)

root.mainloop()
