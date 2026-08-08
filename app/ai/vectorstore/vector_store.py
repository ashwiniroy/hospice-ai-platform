import os

from pinecone import Pinecone


class VectorStore:

    def __init__(self):
        self.pc = Pinecone(
            api_key=os.getenv("PINECONE_API_KEY")
        )

        self.index_name = "hospice-index"

    def get_index(self):
        return self.pc.Index(self.index_name)

    def upsert(
        self,
        vectors: list[dict]
    ):
        index = self.get_index()

        index.upsert(
            vectors=vectors
        )

    def semantic_search(
        self,
        embedding: list[float],
        top_k: int = 5,
        filters: dict | None = None
    ):
        index = self.get_index()

        results = index.query(
            vector=embedding,
            top_k=top_k,
            include_metadata=True,
            filter=filters
        )

        matches = []

        for match in results.matches:
            matches.append({
                "id": match.id,
                "score": float(match.score),
                "metadata": dict(match.metadata or {})
            })

        return matches
    
    
    def upsert(
    self,
    vectors: list[dict]
    ):
     index = self.get_index()

     index.upsert(
        vectors=vectors
     )