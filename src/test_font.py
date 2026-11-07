from PIL import Image, ImageDraw, ImageFont

font = ImageFont.truetype("data/fonts/NotoSansBrahmi-Regular.ttf", 64)
img = Image.new("L", (96, 96), 255)
draw = ImageDraw.Draw(img)
draw.text((16, 8), chr(0x11005), font=font, fill=0)
img.save("data/synthetic/test_A.png")
print("saved")