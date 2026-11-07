import unicodedata
from collections import Counter
import torch
import torch.nn as nn
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, random_split

tf = transforms.Compose([
    transforms.Grayscale(1),
    transforms.Resize((64, 64)),
    transforms.ToTensor(),
    transforms.Normalize((0.5,), (0.5,)),
])
ds = datasets.ImageFolder("data/synthetic/augmented", transform=tf)
n_val = int(0.2 * len(ds))
_, val_ds = random_split(
    ds, [len(ds) - n_val, n_val],
    generator=torch.Generator().manual_seed(42))
val_dl = DataLoader(val_ds, batch_size=64)

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

def name(i):
    return unicodedata.name(chr(int(classes[i], 16)), "?").replace("BRAHMI LETTER ", "")

pairs = Counter()
with torch.no_grad():
    for x, y in val_dl:
        p = model(x).argmax(1)
        for t, q in zip(y.tolist(), p.tolist()):
            if t != q:
                pairs[(t, q)] += 1

print("Most confused (true -> predicted):")
for (t, q), n in pairs.most_common(10):
    print(f"{name(t)} -> {name(q)}: {n} times")