from __future__ import annotations

import json
import os
from dataclasses import dataclass

import faiss
import numpy as np


@dataclass
class _MetaRow:
    asset_id: int


class FaissVectorStore:
    """
    Cosine similarity implemented as inner-product over L2-normalized vectors.
    Persists:
      - FAISS index to `index_path`
      - metadata (asset_id per row) to jsonl `meta_path`
    """

    def __init__(self, *, index_path: str, meta_path: str) -> None:
        self.index_path = index_path
        self.meta_path = meta_path

        self._index: faiss.Index | None = None
        self._meta: list[_MetaRow] = []
        self._dim: int | None = None

        self._load_if_exists()

    def _load_if_exists(self) -> None:
        if os.path.exists(self.index_path) and os.path.exists(self.meta_path):
            self._index = faiss.read_index(self.index_path)
            self._dim = self._index.d
            self._meta = []
            with open(self.meta_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    obj = json.loads(line)
                    self._meta.append(_MetaRow(asset_id=int(obj["asset_id"])))

    def _ensure_index(self, dim: int) -> None:
        if self._index is None:
            self._dim = dim
            self._index = faiss.IndexFlatIP(dim)

    def upsert(self, *, asset_id: int, embedding: list[float]) -> None:
        vec = np.array(embedding, dtype=np.float32)
        if vec.ndim != 1:
            raise ValueError("embedding must be 1D")

        self._ensure_index(dim=int(vec.shape[0]))
        assert self._index is not None and self._dim is not None
        if int(vec.shape[0]) != self._dim:
            raise ValueError(f"Embedding dim mismatch. Expected {self._dim}, got {vec.shape[0]}")

        # Simple upsert strategy: rebuild if exists (OK for demo; for scale use IDMap + remove_ids)
        self.delete(asset_id=asset_id)

        self._index.add(vec.reshape(1, -1))
        self._meta.append(_MetaRow(asset_id=asset_id))

    def delete(self, *, asset_id: int) -> None:
        """
        Removes an asset from the index.
        For simplicity, we rebuild the index without that ID.
        """
        existing_pos = None
        for i, m in enumerate(self._meta):
            if m.asset_id == asset_id:
                existing_pos = i
                break
        if existing_pos is not None:
            self._rebuild_without(asset_id=asset_id)

    def _rebuild_without(self, *, asset_id: int) -> None:
        assert self._index is not None and self._dim is not None
        keep = [i for i, m in enumerate(self._meta) if m.asset_id != asset_id]
        if not keep:
            self._index = faiss.IndexFlatIP(self._dim)
            self._meta = []
            return
        vecs = self._index.reconstruct_n(0, self._index.ntotal)
        vecs_keep = vecs[keep]
        self._index = faiss.IndexFlatIP(self._dim)
        self._index.add(vecs_keep)
        self._meta = [self._meta[i] for i in keep]

    def search(self, *, embedding: list[float], k: int) -> list[dict]:
        if self._index is None or not self._meta:
            return []
        vec = np.array(embedding, dtype=np.float32).reshape(1, -1)
        scores, idxs = self._index.search(vec, k)
        out: list[dict] = []
        for score, idx in zip(scores[0].tolist(), idxs[0].tolist()):
            if idx < 0:
                continue
            out.append({"asset_id": self._meta[idx].asset_id, "score": float(score)})
        return out

    def find_near_duplicate(self, *, embedding: list[float], threshold: float) -> dict | None:
        hits = self.search(embedding=embedding, k=1)
        if not hits:
            return None
        best = hits[0]
        if float(best.get("score") or 0.0) >= float(threshold):
            return {"asset_id": int(best["asset_id"]), "score": float(best["score"])}
        return None

    def persist(self) -> None:
        if self._index is None:
            return
        os.makedirs(os.path.dirname(self.index_path) or ".", exist_ok=True)
        os.makedirs(os.path.dirname(self.meta_path) or ".", exist_ok=True)
        faiss.write_index(self._index, self.index_path)
        with open(self.meta_path, "w", encoding="utf-8") as f:
            for m in self._meta:
                f.write(json.dumps({"asset_id": m.asset_id}) + "\n")

