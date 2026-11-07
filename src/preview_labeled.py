import unicodedata
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = "data/fonts/NotoSansBrahmi-Regular.ttf"
big = ImageFont.truetype(FONT_PATH, 56)
small = ImageFont.load_default()

codes = list(range(0x11005, 0x11035))
cols, cw, ch = 8, 120, 110
rows = (len(codes) + cols - 1) // cols
sheet = Image.new("L", (cols * cw, rows * ch), 255)
d = ImageDraw.Draw(sheet)

for i, code in enumerate(codes):
    x, y = (i % cols) * cw, (i // cols) * ch
    d.text((x + cw // 2, y + 40), chr(code), font=big, fill=0, anchor="mm")
    name = unicodedata.name(chr(code), "?").replace("BRAHMI LETTER ", "")
    d.text((x + 8, y + 82), name, font=small, fill=0)
    d.text((x + 8, y + 96), f"{code:X}", font=small, fill=0)

sheet.save("data/synthetic/preview_labeled.png")
print("saved")