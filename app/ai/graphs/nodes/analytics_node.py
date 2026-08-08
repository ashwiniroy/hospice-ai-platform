from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage

from app.ai.graphs.state import HospiceGraphState
from app.services.analytics_service import AnalyticsService


class AnalyticsNode:

    def __init__(self):
        self.analytics_service = AnalyticsService()

        self.llm = ChatOpenAI(
            model="gpt-4.1-mini",
            temperature=0
        )

    def execute(
        self,
        state: HospiceGraphState
    ):
        question = state.get(
            "resolved_question",
            state["question"]
        )

        summary = self.analytics_service.get_summary()

        prompt = f"""
User question:

{question}

Available hospice analytics:

{summary}

Answer using only the available analytics.
"""

        response = self.llm.invoke(prompt)

        return {
            "answer": response.content,
            "sources": [],
            "messages": [
                AIMessage(content=response.content)
            ]
        }