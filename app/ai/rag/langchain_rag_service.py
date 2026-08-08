from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.ai.rag.retriever import HospiceRetriever


class LangChainRagService:

    def __init__(self):
        self.retriever = HospiceRetriever()

        self.llm = ChatOpenAI(
            model="gpt-4.1-mini",
            temperature=0
        )

        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
You are a hospice provider information assistant.

Answer the user's question using ONLY the supplied hospice provider context.

If the information is not available in the context,
say that the available data does not contain enough information.

Do not invent:
- quality ratings
- rankings
- clinical recommendations
- patient-specific medical advice

Do not interpret vector similarity scores as provider quality.
"""
                ),
                (
                    "human",
                    """
Context:
{context}

Question:
{question}
"""
                )
            ]
        )

        self.parser = StrOutputParser()

        self.chain = (
            self.prompt
            | self.llm
            | self.parser
        )

    def ask(
        self,
        question: str,
        state: str | None = None,
        ownership: str | None = None,
        top_k: int = 5
    ):
        results = self.retriever.retrieve(
            query=question,
            top_k=top_k,
            state=state,
            ownership=ownership
        )

        context_parts = []

        for result in results:
            metadata = result.get("metadata", {})
            text = metadata.get("text", "")

            if text:
                context_parts.append(text)

        context = "\n\n---\n\n".join(context_parts)

        if not context:
            return {
                "question": question,
                "answer": (
                    "The available hospice data does not contain "
                    "enough relevant information to answer this question."
                ),
                "sources": []
            }

        answer = self.chain.invoke(
            {
                "context": context,
                "question": question
            }
        )

        sources = self._build_sources(results)

        return {
            "question": question,
            "answer": answer,
            "sources": sources
        }

    def _build_sources(
        self,
        results: list[dict]
    ):
        sources = []

        for result in results:
            metadata = result.get("metadata", {})

            sources.append({
                "id": result.get("id"),
                "score": result.get("score"),
                "organization_name": metadata.get(
                    "organization_name"
                ),
                "doing_business_as_name": metadata.get(
                    "doing_business_as_name"
                ),
                "city": metadata.get("city"),
                "state": metadata.get("state"),
                "npi": metadata.get("npi"),
                "ccn": metadata.get("ccn"),
                "proprietary_nonprofit": metadata.get(
                    "proprietary_nonprofit"
                )
            })

        return sources