from __future__ import annotations

"""Semantic vector store utilities for Limnus memories."""

import hashlib
import json
import math
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from interface.logger import log_event

try:  # optional dependency
    from sklearn.feature_extraction.text import HashingVectorizer  # type: ignore
except Exception:  # pragma: no cover - optional
    HashingVectorizer = None  # type: ignore

try:  # optional dependency
    from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore
except Exception:  # pragma: no cover
    TfidfVectorizer = None  # type: ignore

try:  # optional dependency
    from sentence_transformers import SentenceTransformer  # type: ignore
except Exception:  # pragma: no cover
    SentenceTransformer = None  # type: ignore

try:  # optional dependency
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None  # type: ignore


STATE_DIR = Path(__file__).resolve().parents[1] / "state"
VECTOR_DIR = STATE_DIR / "vector_store"
VECTOR_DIR.mkdir(parents=True, exist_ok=True)
INDEX_FILE = VECTOR_DIR / "limnus_vectors.json"
CONFIG_DIR = Path(__file__).resolve().parents[1] / "config"
CONFIG_FILE = CONFIG_DIR / "memory.yaml"
DEFAULT_DIMENSIONS = 256


def _load_config() -> Dict[str, Any]:
    if not (yaml and CONFIG_FILE.exists()):
        return {}
    try:
        return yaml.safe_load(CONFIG_FILE.read_text(encoding="utf-8")) or {}
    except Exception:  # pragma: no cover - config optional
        return {}


@dataclass
class VectorEntry:
    """Stored vector plus associated metadata."""

    id: str
    text: str
    vector: List[float]
    metadata: Dict[str, str]


class BaseBackend:
    def embed(self, text: str) -> List[float]:  # pragma: no cover - protocol
        raise NotImplementedError

    def embed_many(self, texts: List[str]) -> List[List[float]]:
        return [self.embed(t) for t in texts]


class HashBackend(BaseBackend):
    """Pure Python hashing embedder (dependency-free)."""

    def __init__(self, dims: int = DEFAULT_DIMENSIONS) -> None:
        self.dims = dims

    def embed(self, text: str) -> List[float]:
        vec = [0.0] * self.dims
        for token in text.lower().split():
            idx = int(hashlib.md5(token.encode()).hexdigest(), 16) % self.dims
            vec[idx] += 1.0
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]


class SklearnHashBackend(BaseBackend):
    """HashingVectorizer backend (requires scikit-learn)."""

    def __init__(self, dims: int = DEFAULT_DIMENSIONS) -> None:
        if HashingVectorizer is None:  # pragma: no cover - defensive
            raise RuntimeError("HashingVectorizer unavailable")
        self.vectorizer = HashingVectorizer(
            n_features=dims,
            alternate_sign=False,
            norm="l2",
        )

    def embed(self, text: str) -> List[float]:
        return self.embed_many([text])[0]

    def embed_many(self, texts: List[str]) -> List[List[float]]:
        matrix = self.vectorizer.transform(texts)
        return matrix.toarray().tolist()


class TFIDFBackend(BaseBackend):
    def __init__(self, dims: int = DEFAULT_DIMENSIONS) -> None:
        if TfidfVectorizer is None:  # pragma: no cover - defensive
            raise RuntimeError("TfidfVectorizer unavailable")
        self.vectorizer = TfidfVectorizer(max_features=dims)

    def embed(self, text: str) -> List[float]:
        return self.embed_many([text])[0]

    def embed_many(self, texts: List[str]) -> List[List[float]]:
        matrix = self.vectorizer.fit_transform(texts)
        return matrix.toarray().tolist()


class SBERTBackend(BaseBackend):
    DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

    def __init__(self, model_name: Optional[str] = None) -> None:
        if SentenceTransformer is None:  # pragma: no cover - defensive
            raise RuntimeError("SentenceTransformer unavailable")
        self.model_name = model_name or self.DEFAULT_MODEL
        try:
            self.model = SentenceTransformer(self.model_name)
        except Exception as exc:  # pragma: no cover - defensive
            raise RuntimeError(f"Unable to load SentenceTransformer: {exc}") from exc

    def embed(self, text: str) -> List[float]:
        return self.embed_many([text])[0]

    def embed_many(self, texts: List[str]) -> List[List[float]]:
        vectors = self.model.encode(texts, show_progress_bar=False)
        return [vec.tolist() for vec in vectors]


class Embedder:
    """Selects the best available backend for text embeddings."""

    def __init__(self, dims: int = DEFAULT_DIMENSIONS, backend: Optional[str] = None) -> None:
        cfg = _load_config().get("embedding", {})
        backend = (backend or os.getenv("KIRA_VECTOR_BACKEND") or cfg.get("backend"))
        backend = str(backend).lower() if backend else self._auto_backend()
        model_name = os.getenv("KIRA_VECTOR_MODEL") or cfg.get("model_name")

        if backend == "tfidf" and TfidfVectorizer is not None:
            self.impl = TFIDFBackend(dims)
            self.backend_name = "tfidf"
        elif backend in {"sbert", "sentence-bert", "sentence_transformer"} and SentenceTransformer is not None:
            self.impl = SBERTBackend(model_name=model_name)
            self.backend_name = "sbert"
        elif backend == "sklearn-hash" and HashingVectorizer is not None:
            self.impl = SklearnHashBackend(dims)
            self.backend_name = "sklearn-hash"
        else:
            self.impl = HashBackend(dims)
            self.backend_name = "hash"

    def embed(self, text: str) -> List[float]:
        return self.impl.embed(text)

    def embed_many(self, texts: List[str]) -> List[List[float]]:
        return self.impl.embed_many(texts)

    # ------------------------------------------------------------------ helpers
    def _auto_backend(self) -> str:
        # Preferred order: TF-IDF -> SBERT -> sklearn hash -> fallback hash
        if TfidfVectorizer is not None:
            return "tfidf"
        if SentenceTransformer is not None:
            return "sbert"
        if HashingVectorizer is not None:
            return "sklearn-hash"
        return "hash"


class VectorStore:
    """Persists memory embeddings for semantic recall."""

    def __init__(
        self,
        index_file: Path = INDEX_FILE,
        dims: int = DEFAULT_DIMENSIONS,
        backend: Optional[str] = None,
    ) -> None:
        self.index_file = index_file
        self.embedder = Embedder(dims=dims, backend=backend)
        self.entries: Dict[str, VectorEntry] = {}
        self._load()
        self._refresh_embeddings()

    def _load(self) -> None:
        if not self.index_file.exists():
            return
        try:
            raw = json.loads(self.index_file.read_text(encoding="utf-8"))
            for item in raw:
                entry = VectorEntry(
                    id=item["id"],
                    text=item.get("text", ""),
                    vector=item.get("vector", []),
                    metadata=item.get("metadata", {}),
                )
                self.entries[entry.id] = entry
        except Exception as exc:  # pragma: no cover - defensive
            log_event("vector_store", "load_error", {"error": str(exc)}, status="error")
            self.entries.clear()

    def _save(self) -> None:
        payload = [
            {
                "id": entry.id,
                "text": entry.text,
                "vector": entry.vector,
                "metadata": entry.metadata,
            }
            for entry in self.entries.values()
        ]
        self.index_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def upsert(
        self,
        text: str,
        entry_id: str,
        metadata: Optional[Dict[str, str]] = None,
    ) -> None:
        entry = self.entries.get(entry_id)
        if entry:
            entry.text = text
            if metadata:
                entry.metadata.update(metadata)
        else:
            entry = VectorEntry(entry_id, text, [], metadata or {})
            self.entries[entry_id] = entry
        self._refresh_embeddings()
        log_event("vector_store", "upsert", {"id": entry_id, "metadata": metadata or {}})

    def ensure_indexed(
        self,
        items: Iterable[Dict[str, str]],
        *,
        text_key: str = "text",
        id_key: str = "id",
    ) -> None:
        changed = False
        for item in items:
            if not isinstance(item, dict):
                continue
            entry_id = item.get(id_key) or item.get("ts") or item.get("timestamp")
            text = item.get(text_key) or item.get("text")
            if not entry_id or not text:
                continue
            tags = item.get("tags") or []
            metadata = {"tags": ",".join(tags) if isinstance(tags, list) else str(tags)}
            existing = self.entries.get(entry_id)
            if existing:
                updated = False
                if existing.text != text:
                    existing.text = text
                    updated = True
                if metadata and metadata != existing.metadata:
                    existing.metadata.update(metadata)
                    updated = True
                if updated:
                    changed = True
                continue
            self.entries[entry_id] = VectorEntry(entry_id, text, [], metadata)
            changed = True
        if changed:
            self._refresh_embeddings()

    def semantic_search(self, text: str, top_k: int = 3) -> List[tuple[float, VectorEntry]]:
        if not text or not self.entries:
            return []
        query_vec = self.embedder.embed(text)

        def similarity(entry: VectorEntry) -> float:
            return float(sum(a * b for a, b in zip(query_vec, entry.vector)))

        ranked = sorted(self.entries.values(), key=similarity, reverse=True)
        return [(similarity(entry), entry) for entry in ranked[:top_k]]

    def _refresh_embeddings(self) -> None:
        if not self.entries:
            self._save()
            return
        texts = [entry.text for entry in self.entries.values()]
        vectors = self.embedder.embed_many(texts)
        for entry, vec in zip(self.entries.values(), vectors):
            entry.vector = vec
        self._save()

    def delete(self, entry_id: str) -> None:
        if entry_id in self.entries:
            del self.entries[entry_id]
            self._save()
            log_event("vector_store", "delete", {"id": entry_id})
