"""
model.py — Arsitektur Neural Collaborative Filtering (NCF).

Embedding pengguna & item -> concatenation -> MLP berlapis (ReLU + Dropout)
-> Output Linear(.. -> 1) + Sigmoid. Sesuai Bab 3 & Tabel 4.9 skripsi.
"""
import torch
import torch.nn as nn


class NCF(nn.Module):
    def __init__(self, n_users, n_items, embed, layers, dropout):
        super().__init__()
        self.user_emb = nn.Embedding(n_users, embed)
        self.item_emb = nn.Embedding(n_items, embed)
        seq = []
        # layers[0] = dimensi concat (2*embed); sisanya hidden layer
        for a, b in zip(layers[:-1], layers[1:]):
            seq += [nn.Linear(a, b), nn.ReLU(), nn.Dropout(dropout)]
        self.mlp = nn.Sequential(*seq)
        self.out = nn.Linear(layers[-1], 1)
        nn.init.normal_(self.user_emb.weight, std=0.01)
        nn.init.normal_(self.item_emb.weight, std=0.01)

    def forward(self, u, i):
        x = torch.cat([self.user_emb(u), self.item_emb(i)], dim=-1)
        return torch.sigmoid(self.out(self.mlp(x))).squeeze(-1)

    def num_params(self):
        return sum(p.numel() for p in self.parameters())
