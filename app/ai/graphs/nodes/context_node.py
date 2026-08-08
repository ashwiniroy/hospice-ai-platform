from langchain_openai import ChatOpenAI

from app.ai.graphs.state import HospiceGraphState


class ContextNode:

    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4.1-mini",
            temperature=0
        )

    def execute(
        self,
        state: HospiceGraphState
    ):
        messages = state.get("messages", [])
        previous_results = state.get("results", [])

        history = []

        for message in messages:
            role = getattr(message, "type", "unknown")
            content = getattr(message, "content", "")

            history.append(
                f"{role}: {content}"
            )

        conversation = "\n".join(history)

        result_summary = []

        for index, provider in enumerate(
            previous_results,
            start=1
        ):
            result_summary.append(
                {
                    "position": index,
                    "organization_name": provider.get(
                        "organization_name"
                    ),
                    "doing_business_as_name": provider.get(
                        "doing_business_as_name"
                    ),
                    "city": provider.get("city"),
                    "state": provider.get("state"),
                    "npi": provider.get("npi"),
                    "ccn": provider.get("ccn")
                }
            )

        prompt = f"""
You resolve follow-up questions in a hospice provider conversation.

Conversation history:

{conversation}

Previous provider results:

{result_summary}

Latest user question:

{state["question"]}

Rewrite the latest question as a complete standalone request.

Preserve relevant constraints from earlier turns such as:
- state
- city
- ownership type
- previously returned providers

If the user refers to:
- "the first two"
- "the second provider"
- "those providers"
- "them"
- "the previous results"

resolve those references using Previous provider results.

Examples:

Previous:
Find nonprofit hospices in Texas.

Latest:
Now focus on Dallas.

Resolved:
Find nonprofit hospice providers in Dallas, Texas.

Previous results:
1. ABC Hospice
2. XYZ Hospice

Latest:
Compare the first two.

Resolved:
Compare ABC Hospice and XYZ Hospice.

Return ONLY the rewritten standalone request.
"""

        response = self.llm.invoke(
            prompt,
            config={
                "run_name": "hospice_context_resolver",
                "tags": [
                    "memory",
                    "context-resolution",
                    "langgraph"
                ]
            }
        )

        return {
            "resolved_question": response.content.strip()
        }