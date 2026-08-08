from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage

from app.ai.graphs.state import HospiceGraphState


class GeneralInfoNode:

    def __init__(self):

        self.llm = ChatOpenAI(
            model="gpt-4.1-mini",
            temperature=0
        )

    def execute(
        self,
        state: HospiceGraphState
    ):

        # Use resolved conversational question if available
        question = state.get(
            "resolved_question",
            state["question"]
        )

        prompt = f"""
You are a hospice-care information assistant.

Answer the following general informational question:

{question}

Do not provide patient-specific diagnosis
or treatment advice.
"""

        response = self.llm.invoke(prompt)

        return {
            "answer": response.content,
            "sources": [],

            # Store assistant response in conversation memory
            "messages": [
                AIMessage(content=response.content)
            ]
        }