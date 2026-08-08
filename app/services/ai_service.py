from app.ai.rag.manual_rag_service import ManualRagService
from app.ai.rag.langchain_rag_service import LangChainRagService
from app.ai.graphs.hospice_graph import HospiceGraph


class AIService:

    def __init__(self):
        self.manual_rag = ManualRagService()
        self.langchain_rag = LangChainRagService()
        self.langgraph = HospiceGraph()

    def ask(
        self,
        question: str,
        state: str | None = None,
        ownership: str | None = None,
        top_k: int = 5,
        thread_id: str | None = None,
        mode: str = "manual"
    ):

        if mode == "langgraph":
            return self.langgraph.ask(
                question=question,
                state=state,
                ownership=ownership,
                thread_id=thread_id or "default",
                top_k=top_k
            )

        if mode == "langchain":
            return self.langchain_rag.ask(
                question=question,
                state=state,
                ownership=ownership,
                top_k=top_k
            )

        return self.manual_rag.ask(
            question=question,
            state=state,
            ownership=ownership,
            top_k=top_k
        )