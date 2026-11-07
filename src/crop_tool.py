import os, sys, glob, unicodedata
import cv2

files = sorted(glob.glob("data/real/raw/*.*"))
files = [f for f in files if f.lower().endswith((".jpg", ".jpeg", ".png"))]
i = int(sys.argv[1]) if len(sys.argv) > 1 else 0
path = files[i]
print("photo:", path)

img = cv2.imread(path)
scale = min(1.0, 900 / img.shape[0], 1400 / img.shape[1])
show = cv2.resize(img, None, fx=scale, fy=scale)

while True:
    x, y, w, h = cv2.selectROI("crop", show, showCrosshair=False)
    if w == 0 or h == 0:
        break
    name = input("Letter name (like KA), or blank to skip: ").strip().upper()
    if not name:
        continue
    try:
        ch = unicodedata.lookup("BRAHMI LETTER " + name)
    except KeyError:
        print("Unknown name, try again")
        continue
    code = f"{ord(ch):X}"
    folder = f"data/real/crops/{code}"
    os.makedirs(folder, exist_ok=True)
    crop = img[int(y / scale):int((y + h) / scale), int(x / scale):int((x + w) / scale)]
    n = len(os.listdir(folder))
    cv2.imwrite(f"{folder}/{i}_{n}.png", crop)
    print("saved", name, code)

cv2.destroyAllWindows()