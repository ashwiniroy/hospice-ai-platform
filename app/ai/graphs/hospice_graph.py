from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

from app.ai.graphs.state import HospiceGraphState
from app.ai.graphs.router import HospiceRouter

from app.ai.graphs.nodes.context_node import ContextNode
from app.ai.graphs.nodes.provider_search_node import ProviderSearchNode
from app.ai.graphs.nodes.analytics_node import AnalyticsNode
from app.ai.graphs.nodes.general_info_node import GeneralInfoNode
from app.ai.graphs.nodes.comparison_node import ComparisonNode


class HospiceGraph:

    def __init__(self):
        self.router = HospiceRouter()

        self.context = ContextNode()
        self.provider_search = ProviderSearchNode()
        self.comparison = ComparisonNode()
        self.analytics = AnalyticsNode()
        self.general_info = GeneralInfoNode()

        self.checkpointer = InMemorySaver()

        self.graph = self._build_graph()

    def choose_route(
        self,
        state: HospiceGraphState
    ):
        return state["intent"]

    def _build_graph(self):
        builder = StateGraph(
            HospiceGraphState
        )

        # -------------------------
        # Nodes
        # -------------------------

        builder.add_node(
            "context",
            self.context.execute
        )

        builder.add_node(
            "router",
            self.router.route
        )

        builder.add_node(
            "provider_search",
            self.provider_search.execute
        )

        builder.add_node(
            "comparison",
            self.comparison.execute
        )

        builder.add_node(
            "analytics",
            self.analytics.execute
        )

        builder.add_node(
            "general_info",
            self.general_info.execute
        )

        # -------------------------
        # Flow
        # -------------------------

        builder.add_edge(
            START,
            "context"
        )

        builder.add_edge(
            "context",
            "router"
        )

        builder.add_conditional_edges(
            "router",
            self.choose_route,
            {
                "provider_search": "provider_search",
                "comparison": "comparison",
                "analytics": "analytics",
                "general_info": "general_info"
            }
        )

        # -------------------------
        # Terminal edges
        # -------------------------

        builder.add_edge(
            "provider_search",
            END
        )

        builder.add_edge(
            "comparison",
            END
        )

        builder.add_edge(
            "analytics",
            END
        )

        builder.add_edge(
            "general_info",
            END
        )

        return builder.compile(
            checkpointer=self.checkpointer
        )

    def ask(
        self,
        question: str,
        thread_id: str,
        state: str | None = None,
        ownership: str | None = None,
        top_k: int = 5
    ):
        graph_input = {
            "messages": [
                {
                    "role": "user",
                    "content": question
                }
            ],
            "question": question,
            "top_k": top_k
        }

        # Do not overwrite remembered filters with None
        if state is not None:
            graph_input["state_filter"] = state

        if ownership is not None:
            graph_input["ownership"] = ownership

        result = self.graph.invoke(
            graph_input,
            config={
                "configurable": {
                    "thread_id": thread_id
                },
                "run_name": "hospice_langgraph_memory",
                "tags": [
                    "hospice-ai",
                    "langgraph",
                    "memory"
                ]
            }
        )

        return {
            "question": question,
            "answer": result["answer"],
            "sources": result.get("sources", [])
        }