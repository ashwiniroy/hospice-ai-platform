from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.ai.graphs.state import HospiceGraphState


class HospiceRouter:

    def __init__(self):

        llm = ChatOpenAI(
            model="gpt-4.1-mini",
            temperature=0
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
Classify the user's request into exactly one category:

provider_search
comparison
analytics
general_info

provider_search:
Find, search or discover hospice providers.

comparison:
Compare previously identified hospice providers
or compare specific named hospice providers.

analytics:
Counts, totals, statistics or numerical questions
about hospice providers.

general_info:
General hospice-care questions that do not require
provider dataset search.

Return ONLY the category name.
"""
                ),
                (
                    "human",
                    "{question}"
                )
            ]
        )

        self.chain = (
            prompt
            | llm
            | StrOutputParser()
        )

    def route(
        self,
        state: HospiceGraphState
    ):
        question = state.get(
            "resolved_question",
            state["question"]
        )

        intent = self.chain.invoke(
            {
                "question": question
            },
            config={
                "run_name": "hospice_intent_router",
                "tags": [
                    "router",
                    "langgraph"
                ]
            }
        )

        intent = intent.strip()

        allowed_intents = {
            "provider_search",
            "comparison",
            "analytics",
            "general_info"
        }

        if intent not in allowed_intents:
            intent = "general_info"

        return {
            "intent": intent
        }