#!/usr/bin/env python3
"""
Membuat Gambar 4.1: kurva Training Loss & HR@10 per epoch (Konfigurasi C).
Membaca scripts/history_configC.csv -> figures/gambar_4_1_kurva_training.png
"""
import os, csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CSV = os.path.join(HERE, "history_configC.csv")
OUTDIR = os.path.join(ROOT, "figures")
OUT = os.path.join(OUTDIR, "gambar_4_1_kurva_training.png")

os.makedirs(OUTDIR, exist_ok=True)
ep, loss, hr = [], [], []
best_ep = None
with open(CSV) as f:
    for row in csv.DictReader(f):
        ep.append(int(row["epoch"]))
        loss.append(float(row["training_loss"]))
        hr.append(float(row["hr_at_10"]))
        if "terbaik tersimpan" in row["keterangan"]:
            best_ep = int(row["epoch"])

fig, ax1 = plt.subplots(figsize=(8, 4.5))
ax1.set_xlabel("Epoch")
ax1.set_ylabel("Training Loss", color="#c0392b")
l1, = ax1.plot(ep, loss, "o-", color="#c0392b", label="Training Loss")
ax1.tick_params(axis="y", labelcolor="#c0392b")
ax1.set_xticks(ep)

ax2 = ax1.twinx()
ax2.set_ylabel("HR@10", color="#1a7a3e")
l2, = ax2.plot(ep, hr, "s-", color="#1a7a3e", label="HR@10")
ax2.tick_params(axis="y", labelcolor="#1a7a3e")

# tandai epoch terbaik
last_best = max([e for e in ep if e == best_ep] or [None]) if best_ep else None
# epoch terbaik = epoch dengan HR tertinggi (model terbaik terakhir tersimpan)
hr_best_ep = ep[hr.index(max(hr))]
ax2.axvline(hr_best_ep, ls="--", color="gray", alpha=0.6)
ax2.annotate(f"Model terbaik\n(epoch {hr_best_ep}, HR={max(hr):.4f})",
             xy=(hr_best_ep, max(hr)), xytext=(hr_best_ep + 0.3, max(hr) - 0.004),
             fontsize=8, color="gray")

plt.title("Kurva Training Loss dan HR@10 — Konfigurasi C (Skenario B)")
lines = [l1, l2]
ax1.legend(lines, [ln.get_label() for ln in lines], loc="center right")
fig.tight_layout()
fig.savefig(OUT, dpi=150)
print(f"OK -> {OUT}")
