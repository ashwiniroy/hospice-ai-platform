from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages


class HospiceGraphState(TypedDict, total=False):

    messages: Annotated[
        list,
        add_messages
    ]

    question: str
    resolved_question: str

    state_filter: str | None
    ownership: str | None
    top_k: int

    intent: str

    results: list[dict]

    answer: str
    sources: list[dict]