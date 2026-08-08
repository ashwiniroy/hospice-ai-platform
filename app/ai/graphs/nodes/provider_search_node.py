from langchain_core.messages import AIMessage

from app.ai.graphs.state import HospiceGraphState
from app.ai.rag.langchain_rag_service import LangChainRagService


class ProviderSearchNode:

    def __init__(self):
        self.rag_service = LangChainRagService()

    def execute(
        self,
        state: HospiceGraphState
    ):
        question = state.get(
            "resolved_question",
            state["question"]
        )

        response = self.rag_service.ask(
            question=question,
            state=state.get("state_filter"),
            ownership=state.get("ownership"),
            top_k=state.get("top_k", 5)
        )

        answer = response["answer"]
        sources = response["sources"]

        return {
            "answer": answer,
            "sources": sources,
            "results": sources,

            # IMPORTANT
            "messages": [
                AIMessage(content=answer)
            ]
        }