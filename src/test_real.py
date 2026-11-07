import glob, os, unicodedata
import torch
import torch.nn as nn
from PIL import Image
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

def square(img):
    img = img.convert("L")
    w, h = img.size
    s = max(w, h)
    px = sorted(img.getdata())
    bg = px[len(px) // 2]
    out = Image.new("L", (s, s), bg)
    out.paste(img, ((s - w) // 2, (s - h) // 2))
    return out

def name(code):
    return unicodedata.name(chr(int(code, 16)), "?").replace("BRAHMI LETTER ", "")

total = top1 = top3 = 0
wrong = []
for folder in sorted(glob.glob("data/real/crops/*")):
    code = os.path.basename(folder)
    if code not in classes:
        continue
    true_idx = classes.index(code)
    for f in sorted(glob.glob(folder + "/*.png")):
        x = tf(square(Image.open(f))).unsqueeze(0)
        with torch.no_grad():
            probs = model(x)[0]
        order = probs.argsort(descending=True).tolist()
        total += 1
        top1 += order[0] == true_idx
        top3 += true_idx in order[:3]
        if order[0] != true_idx:
            wrong.append(f"{name(code)} -> {name(classes[order[0]])}")

print("real crops tested:", total)
print(f"top-1 accuracy: {top1 / total:.3f}")
print(f"top-3 accuracy: {top3 / total:.3f}")
print("wrong ones (true -> predicted):")
for w in wrong:
    print(w)