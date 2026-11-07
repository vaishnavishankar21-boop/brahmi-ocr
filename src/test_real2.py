import glob, os
import numpy as np
import torch
import torch.nn as nn
from PIL import Image, ImageOps
from torchvision import transforms

ck = torch.load("models/baseline.pt")
classes = ck["classes"]
model = nn.Sequential(
    nn.Conv2d(1, 16, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
    nn.Conv2d(16, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
    nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
    nn.Flatten(),
    nn.Linear(64 * 8 * 8, 128), nn.ReLU(),
    nn.Linear(128, len(classes)),
)
model.load_state_dict(ck["model"])
model.eval()

tf = transforms.Compose([
    transforms.Resize((64, 64)),
    transforms.ToTensor(),
    transforms.Normalize((0.5,), (0.5,)),
])

def square(img, auto, margin):
    img = img.convert("L")
    if auto:
        img = ImageOps.autocontrast(img, cutoff=2)
    w, h = img.size
    s = int(max(w, h) * margin)
    bg = int(np.median(np.array(img)))
    out = Image.new("L", (s, s), bg)
    out.paste(img, ((s - w) // 2, (s - h) // 2))
    return out

items = []
for folder in sorted(glob.glob("data/real/crops/*")):
    code = os.path.basename(folder)
    if code in classes:
        for f in sorted(glob.glob(folder + "/*.png")):
            items.append((f, classes.index(code)))
print("real crops:", len(items))

def evaluate(auto, margin):
    top1 = top3 = 0
    for f, t in items:
        x = tf(square(Image.open(f), auto, margin)).unsqueeze(0)
        with torch.no_grad():
            order = model(x)[0].argsort(descending=True).tolist()
        top1 += order[0] == t
        top3 += t in order[:3]
    return top1 / len(items), top3 / len(items)

for auto, margin in [(False, 1.0), (True, 1.0), (False, 1.5), (True, 1.5)]:
    a, b = evaluate(auto, margin)
    print(f"autocontrast={auto} margin={margin} | top-1 {a:.3f} | top-3 {b:.3f}")