import os
import torch
import torch.nn as nn
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, random_split

torch.manual_seed(42)

tf = transforms.Compose([
    transforms.Grayscale(1),
    transforms.Resize((64, 64)),
    transforms.ToTensor(),
    transforms.Normalize((0.5,), (0.5,)),
])

ds = datasets.ImageFolder("data/synthetic/augmented", transform=tf)
n_val = int(0.2 * len(ds))
train_ds, val_ds = random_split(
    ds, [len(ds) - n_val, n_val],
    generator=torch.Generator().manual_seed(42))
train_dl = DataLoader(train_ds, batch_size=64, shuffle=True)
val_dl = DataLoader(val_ds, batch_size=64)
print("classes:", len(ds.classes), "| train:", len(train_ds), "| val:", len(val_ds))

model = nn.Sequential(
    nn.Conv2d(1, 16, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
    nn.Conv2d(16, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
    nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
    nn.Flatten(),
    nn.Linear(64 * 8 * 8, 128), nn.ReLU(),
    nn.Linear(128, len(ds.classes)),
)
opt = torch.optim.Adam(model.parameters(), lr=1e-3)
loss_fn = nn.CrossEntropyLoss()

for epoch in range(1, 11):
    model.train()
    for x, y in train_dl:
        opt.zero_grad()
        loss_fn(model(x), y).backward()
        opt.step()
    model.eval()
    correct = 0
    with torch.no_grad():
        for x, y in val_dl:
            correct += (model(x).argmax(1) == y).sum().item()
    print(f"epoch {epoch}/10 | val accuracy: {correct / len(val_ds):.3f}")

os.makedirs("models", exist_ok=True)
torch.save({"model": model.state_dict(), "classes": ds.classes}, "models/baseline.pt")
print("saved models/baseline.pt")