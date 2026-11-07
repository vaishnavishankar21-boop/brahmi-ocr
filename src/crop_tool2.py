import os, sys, glob, unicodedata
import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk

files = sorted(glob.glob("data/real/raw/*.*"))
files = [f for f in files if f.lower().endswith((".jpg", ".jpeg", ".png"))]
idx = int(sys.argv[1]) if len(sys.argv) > 1 else 0
path = files[idx]
print("photo:", path)

root = tk.Tk()
root.title(f"Photo {idx}: drag a box, type the letter name. Close window when done.")
img = Image.open(path).convert("RGB")
scale = min(1.0, 800 / img.height, 1300 / img.width)
shown = img.resize((int(img.width * scale), int(img.height * scale)))
photo = ImageTk.PhotoImage(shown)
canvas = tk.Canvas(root, width=shown.width, height=shown.height)
canvas.pack()
canvas.create_image(0, 0, anchor="nw", image=photo)
state = {"x0": 0, "y0": 0, "rect": None}

def down(e):
    state["x0"], state["y0"] = e.x, e.y
    state["rect"] = canvas.create_rectangle(e.x, e.y, e.x, e.y, outline="red", width=2)

def drag(e):
    canvas.coords(state["rect"], state["x0"], state["y0"], e.x, e.y)

def up(e):
    x0, x1 = sorted((state["x0"], e.x))
    y0, y1 = sorted((state["y0"], e.y))
    if x1 - x0 < 5 or y1 - y0 < 5:
        canvas.delete(state["rect"])
        return
    name = simpledialog.askstring("Letter", "Letter name (like KA). Cancel to skip:", parent=root)
    if not name:
        canvas.delete(state["rect"])
        return
    try:
        ch = unicodedata.lookup("BRAHMI LETTER " + name.strip().upper())
    except KeyError:
        messagebox.showerror("Unknown", "Unknown name, try again")
        canvas.delete(state["rect"])
        return
    code = f"{ord(ch):X}"
    folder = f"data/real/crops/{code}"
    os.makedirs(folder, exist_ok=True)
    n = len(os.listdir(folder))
    crop = img.crop((int(x0 / scale), int(y0 / scale), int(x1 / scale), int(y1 / scale)))
    crop.save(f"{folder}/{idx}_{n}.png")
    canvas.itemconfig(state["rect"], outline="lime")
    print("saved", name.upper(), code)

canvas.bind("<ButtonPress-1>", down)
canvas.bind("<B1-Motion>", drag)
canvas.bind("<ButtonRelease-1>", up)
root.mainloop()