from app.services.hospice_service import HospiceService


class HospiceRetriever:

    def __init__(self):
        self.hospice_service = HospiceService()

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        state: str | None = None,
        ownership: str | None = None,
        min_score: float = 0.50
    ):
        results = self.hospice_service.semantic_search(
            query=query,
            top_k=top_k,
            state=state,
            ownership=ownership
        )

        filtered_results = [
            result
            for result in results
            if result["score"] >= min_score
        ]

        return filtered_results