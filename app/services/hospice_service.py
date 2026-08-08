import pandas as pd

from app.services.dataset_service import DatasetService
from app.ai.embeddings.embedding_service import EmbeddingService
from app.ai.vectorstore.vector_store import VectorStore
from langgraph.checkpoint.memory import InMemorySaver


class HospiceService:

    def __init__(self):
        self.dataset_service = DatasetService()
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()

    def get_hospice_by_index(self, index: int):
        df = self.dataset_service.load_hospice_dataset()

        if index < 0 or index >= len(df):
            return None

        record = df.iloc[index].copy()

        record = record.astype(object)
        record = record.where(pd.notnull(record), None)

        return record.to_dict()

    def semantic_search(
        self,
        query: str,
        top_k: int = 5,
        state: str | None = None,
        ownership: str | None = None
    ):
        query_embedding = (
            self.embedding_service
            .generate_embedding(query)
        )

        filters = {}

        if state:
            filters["state"] = {
                "$eq": state.upper()
            }

        if ownership:
            filters["proprietary_nonprofit"] = {
                "$eq": ownership
            }

        results = self.vector_store.semantic_search(
            embedding=query_embedding,
            top_k=top_k,
            filters=filters if filters else None
        )

        return results