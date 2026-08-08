from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage

from app.ai.graphs.state import HospiceGraphState


class ComparisonNode:

    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4.1-mini",
            temperature=0
        )

    def execute(
        self,
        state: HospiceGraphState
    ):
        previous_results = state.get("results", [])

        question = state.get(
            "resolved_question",
            state["question"]
        )

        if len(previous_results) < 2:
            answer = (
                "I don't have enough previously retrieved hospice "
                "providers to perform a comparison."
            )

            return {
                "answer": answer,
                "sources": previous_results,
                "messages": [
                    AIMessage(content=answer)
                ]
            }

        provider_context = []

        for index, provider in enumerate(
            previous_results,
            start=1
        ):
            provider_context.append(
                f"""
Provider {index}

Organization Name:
{provider.get("organization_name")}

Doing Business As:
{provider.get("doing_business_as_name")}

City:
{provider.get("city")}

State:
{provider.get("state")}

NPI:
{provider.get("npi")}

CCN:
{provider.get("ccn")}

Ownership:
{provider.get("proprietary_nonprofit")}

Similarity Score:
{provider.get("score")}
"""
            )

        context = "\n\n---\n\n".join(
            provider_context
        )

        prompt = f"""
You are comparing hospice provider records.

User request:

{question}

Available providers:

{context}

Compare only using the information provided above.

Focus on:
- organization name
- business name
- location
- ownership type
- NPI
- CCN

Do NOT claim that one provider has better clinical quality.

Do NOT interpret vector similarity scores as healthcare quality scores.

If the available information cannot support a requested comparison,
state that clearly.
"""

        response = self.llm.invoke(
            prompt,
            config={
                "run_name": "hospice_provider_comparison",
                "tags": [
                    "comparison",
                    "langgraph"
                ]
            }
        )

        return {
            "answer": response.content,
            "sources": previous_results,
            "messages": [
                AIMessage(
                    content=response.content
                )
            ]
        }