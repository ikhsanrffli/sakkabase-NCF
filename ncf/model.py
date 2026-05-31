"""
NCF — Neural Collaborative Filtering (He et al., 2017).

Arsitektur MLP-based:
  User Embedding (64) ─┐
                        ├─ concat (128) ─ Linear(128→64) ─ ReLU ─ Dropout
  Item Embedding (64) ─┘               ─ Linear(64→32)  ─ ReLU ─ Dropout
                                        ─ Linear(32→1)   ─ Sigmoid
"""

import torch
import torch.nn as nn

from ncf.config import EMBEDDING_DIM, MLP_LAYERS, DROPOUT


class NCF(nn.Module):

    def __init__(
        self,
        n_users:    int,
        n_items:    int,
        embed_dim:  int   = EMBEDDING_DIM,
        mlp_layers: list  = MLP_LAYERS,
        dropout:    float = DROPOUT,
    ):
        super().__init__()

        self.user_embedding = nn.Embedding(n_users, embed_dim)
        self.item_embedding = nn.Embedding(n_items, embed_dim)

        # MLP: input dim = mlp_layers[0] = embed_dim * 2 = 128
        layers = []
        in_dim = mlp_layers[0]
        for out_dim in mlp_layers[1:]:        # 64, 32
            layers += [
                nn.Linear(in_dim, out_dim),
                nn.ReLU(),
                nn.Dropout(dropout),
            ]
            in_dim = out_dim
        layers.append(nn.Linear(in_dim, 1))   # 32 → 1

        self.mlp     = nn.Sequential(*layers)
        self.sigmoid = nn.Sigmoid()

        self._init_weights()

    def _init_weights(self):
        nn.init.normal_(self.user_embedding.weight, std=0.01)
        nn.init.normal_(self.item_embedding.weight, std=0.01)
        for m in self.mlp.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                nn.init.zeros_(m.bias)

    def forward(
        self,
        user_ids: torch.Tensor,
        item_ids: torch.Tensor,
    ) -> torch.Tensor:
        u = self.user_embedding(user_ids)   # (B, 64)
        i = self.item_embedding(item_ids)   # (B, 64)
        x = torch.cat([u, i], dim=-1)       # (B, 128)
        return self.sigmoid(self.mlp(x)).squeeze(-1)
