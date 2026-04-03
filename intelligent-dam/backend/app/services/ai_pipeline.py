from __future__ import annotations

from dataclasses import dataclass

from app.core.config import settings


@dataclass(frozen=True)
class AiResult:
    embedding: list[float]
    tags: list[dict]  # [{name, confidence, source}]
    duplicate: dict | None  # {asset_id, score}


class AiPipeline:
    """
    Thin wrapper over the ai_service package.
    Ensure your PYTHONPATH includes the project root so `ai_service` is importable.
    """

    def __init__(self) -> None:
        self._enabled = False
        self._embedder = None
        self._tagger = None
        self._vector = None

    def _lazy_init(self) -> bool:
        if self._enabled:
            return True
        if self._enabled is False and self._embedder is not None:
            return False # already tried and failed

        print("Initializing AI Pipeline (lazy)...")
        try:
            from ai_service.ai.clip_embedder import ClipEmbedder
            from ai_service.ai.tagger import AutoTagger
            from ai_service.vector_store.faiss_store import FaissVectorStore

            print("Loading models...")
            self._embedder = ClipEmbedder(model_name=settings.CLIP_MODEL_NAME, device=settings.DEVICE)
            self._tagger = AutoTagger(
                clip_embedder=self._embedder,
                zero_shot_model_name=settings.ZERO_SHOT_MODEL_NAME,
                device=settings.DEVICE,
            )
            self._vector = FaissVectorStore(
                index_path=settings.FAISS_INDEX_PATH,
                meta_path=settings.FAISS_META_PATH,
            )
            self._dup_threshold = settings.DUPLICATE_SIM_THRESHOLD
            self._enabled = True
            print("AI Service enabled.")
            return True
        except Exception as e:
            print(f"AI Service disabled due to error: {e}")
            self._enabled = False
            self._embedder = "failed" # mark as failed
            return False

    def process_asset(self, *, asset_id: int, bytes_: bytes, content_type: str) -> AiResult:
        if not self._lazy_init():
            return AiResult(embedding=[], tags=[], duplicate=None)

        emb = self._embedder.embed_asset(bytes_=bytes_, content_type=content_type)
        tags = self._tagger.generate_tags(bytes_=bytes_, content_type=content_type)

        dup = self._vector.find_near_duplicate(embedding=emb, threshold=self._dup_threshold)
        self._vector.upsert(asset_id=asset_id, embedding=emb)
        self._vector.persist()

        return AiResult(
            embedding=emb,
            tags=tags,
            duplicate=dup,
        )

    def semantic_search(self, *, query: str, k: int) -> list[dict]:
        if not self._lazy_init():
            return []
        q = self._embedder.embed_text(query)
        return self._vector.search(embedding=q, k=k)

    def delete_asset(self, *, asset_id: int) -> None:
        if self._lazy_init():
            self._vector.delete(asset_id=asset_id)
            self._vector.persist()



ai_pipeline = AiPipeline()

