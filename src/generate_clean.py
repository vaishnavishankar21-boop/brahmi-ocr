import os
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = "data/fonts/NotoSansBrahmi-Regular.ttf"
OUT_DIR = "data/synthetic/clean"
os.makedirs(OUT_DIR, exist_ok=True)

font = ImageFont.truetype(FONT_PATH, 64)
codes = range(0x11005, 0x11035)  # 48 Brahmi letters

for code in codes:
    img = Image.new("L", (96, 96), 255)
    draw = ImageDraw.Draw(img)
    draw.text((48, 48), chr(code), font=font, fill=0, anchor="mm")
    img.save(f"{OUT_DIR}/{code:X}.png")

print("saved", len(codes), "images")