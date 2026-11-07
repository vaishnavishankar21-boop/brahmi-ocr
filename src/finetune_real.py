import glob, os, random
import numpy as np
import torch
import torch.nn as nn
from PIL import Image, ImageOps
from torchvision import datasets, transforms
from torch.utils.data import Dataset, DataLoader, ConcatDataset

random.seed(42)
torch.manual_seed(42)

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

tf = transforms.Compose([
    transforms.Resize((64, 64)),
    transforms.ToTensor(),
    transforms.Normalize((0.5,), (0.5,)),
])

def square(img):
    img = ImageOps.autocontrast(img.convert("L"), cutoff=2)
    w, h = img.size
    s = int(max(w, h) * 1.2)
    bg = int(np.median(np.array(img)))
    out = Image.new("L", (s, s), bg)
    out.paste(img, ((s - w) // 2, (s - h) // 2))
    return out

items = []
for folder in sorted(glob.glob("data/real/crops/*")):
    code = os.path.basename(folder)
    if code in classes:
        for f in sorted(glob.glob(folder + "/*.png")):
            photo = int(os.path.basename(f).split("_")[0])
            items.append((f, classes.index(code), photo))

counts = {}
for _, _, p in items:
    counts[p] = counts.get(p, 0) + 1
test_photos, got = set(), 0
for p in sorted(counts, reverse=True):
    if got >= 0.25 * len(items):
        break
    test_photos.add(p)
    got += counts[p]

train_items = [(f, y) for f, y, p in items if p not in test_photos]
test_items = [(f, y) for f, y, p in items if p in test_photos]
print("test photos:", sorted(test_photos))
print("real train crops:", len(train_items), "| real test crops:", len(test_items))

class Real(Dataset):
    def __init__(self, data, train):
        self.data, self.train = data, train
        self.aug = transforms.RandomAffine(10, translate=(0.08, 0.08), scale=(0.85, 1.1), fill=128)
    def __len__(self):
        return len(self.data)
    def __getitem__(self, i):
        f, y = self.data[i]
        img = square(Image.open(f))
        if self.train:
            img = self.aug(img)
        return tf(img), y

synth = datasets.ImageFolder(
    "data/synthetic/augmented",
    transform=transforms.Compose([transforms.Grayscale(1), tf]))
train_ds = ConcatDataset([synth] + [Real(train_items, True)] * 10)
train_dl = DataLoader(train_ds, batch_size=64, shuffle=True)
test_dl = DataLoader(Real(test_items, False), batch_size=64)

def evaluate():
    model.eval()
    top1 = top3 = 0
    with torch.no_grad():
        for x, y in test_dl:
            top = model(x).topk(3, dim=1).indices
            top1 += (top[:, 0] == y).sum().item()
            top3 += (top == y.unsqueeze(1)).any(dim=1).sum().item()
    return top1 / len(test_items), top3 / len(test_items)

a, b = evaluate()
print(f"before fine-tuning | test top-1 {a:.3f} | top-3 {b:.3f}")

opt = torch.optim.Adam(model.parameters(), lr=3e-4)
loss_fn = nn.CrossEntropyLoss()
for epoch in range(1, 9):
    model.train()
    for x, y in train_dl:
        opt.zero_grad()
        loss_fn(model(x), y).backward()
        opt.step()
    a, b = evaluate()
    print(f"epoch {epoch}/8 | test top-1 {a:.3f} | top-3 {b:.3f}")

torch.save({"model": model.state_dict(), "classes": classes}, "models/finetuned.pt")
print("saved models/finetuned.pt")