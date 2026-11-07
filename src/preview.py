from PIL import Image
import glob

files = sorted(glob.glob("data/synthetic/clean/*.png"))
cols = 8
rows = (len(files) + cols - 1) // cols
sheet = Image.new("L", (cols * 96, rows * 96), 255)
for i, f in enumerate(files):
    sheet.paste(Image.open(f), ((i % cols) * 96, (i // cols) * 96))
sheet.save("data/synthetic/preview.png")
print("saved preview")