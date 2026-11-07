import glob, os, unicodedata
from PIL import Image, ImageDraw

CELL = 80
folders = sorted(glob.glob("data/real/crops/*"))
sheet = Image.new("L", (90 + 7 * CELL, len(folders) * CELL), 255)
d = ImageDraw.Draw(sheet)

def name(code):
    return unicodedata.name(chr(int(code, 16)), "?").replace("BRAHMI LETTER ", "")

for r, folder in enumerate(folders):
    code = os.path.basename(folder)
    y = r * CELL
    d.text((4, y + 32), name(code), fill=0)
    clean = f"data/synthetic/clean/{code}.png"
    if os.path.exists(clean):
        sheet.paste(Image.open(clean).convert("L").resize((CELL, CELL)), (90, y))
    for c, f in enumerate(sorted(glob.glob(folder + "/*.png"))[:6]):
        im = Image.open(f).convert("L")
        im.thumbnail((CELL - 4, CELL - 4))
        sheet.paste(im, (90 + (c + 1) * CELL + 2, y + 2))

sheet.save("data/real/crops_sheet.png")
print("saved data/real/crops_sheet.png")