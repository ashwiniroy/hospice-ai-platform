# Hospice AI Platform --- Development Progress

## Project Goal

Build an AI-enabled hospice provider information platform with FastAPI
and a public hospice enrollment dataset while learning the major layers
of modern AI Engineering: embeddings, vector databases, semantic search,
RAG, LangChain, LangGraph, conversational memory, specialized workflows,
and LangSmith observability.

## Current Architecture

``` text
Client / Swagger
      |
      v
   FastAPI
      |
      v
  AIService
      |
 +----+----------------+
 |         |           |
 v         v           v
Manual   LangChain   LangGraph
 RAG       RAG          |
 |          |           |
 +----------+-----------+
            |
            v
     Hospice Services
            |
     +------+------+
     |             |
     v             v
 Embeddings     Analytics
     |
     v
  Pinecone
     |
     v
HHS Hospice Enrollment Dataset

LangGraph:
Context -> Router -> Provider Search / Comparison / Analytics / General Info

LangSmith:
Tracing and observability
```

## 1. FastAPI Foundation

A layered FastAPI project was created with API routes, services,
schemas, AI components, scripts, tests, notebooks, and evaluation
folders.

Important areas include:

``` text
app/
├── main.py
├── api/routes/
├── schemas/
├── services/
└── ai/
    ├── embeddings/
    ├── vectorstore/
    ├── rag/
    ├── graphs/
    ├── tools/
    └── prompts/
```

The API layer is kept separate from AI/business logic.

## 2. Dataset Integration

The project uses the HHS hospice enrollment dataset.

Important columns identified include:

``` text
enrollment_id
enrollment_state
provider_type_code
provider_type_text
npi
multiple_npi_flag
ccn
associate_id
organization_name
doing_business_as_name
incorporation_date
incorporation_state
organization_type_structure
organization_other_type_text
proprietary_nonprofit
address_line_1
address_line_2
city
state
zip_code
```

A `DatasetService` was created as the central dataset-loading layer.

During integration we resolved issues involving the Hugging Face
`datasets` package, CSV/encoding and schema loading, `DatasetDict`
versus Pandas DataFrame handling, and JSON serialization of `NaN`
values.

## 3. Hospice Service Layer

`HospiceService` handles provider-oriented operations including:

-   Loading hospice records.
-   Getting a hospice by dataset index.
-   Converting Pandas values to JSON-safe values.
-   Generating query embeddings.
-   Performing semantic search.
-   Passing metadata filters to Pinecone.

## 4. Analytics

An `AnalyticsService` was implemented for deterministic calculations
rather than asking an LLM to calculate dataset statistics.

Implemented analytics include:

-   Total hospice records.
-   Total states.
-   Total cities.
-   Nonprofit provider count.
-   Hospice counts by state.
-   Organization structure/type counts.

## 5. Pinecone Vector Database

PostgreSQL was intentionally skipped for the AI retrieval layer and
Pinecone was adopted as the vector database.

``` text
Hospice Provider Data
        |
        v
Text Representation
        |
        v
OpenAI Embeddings
        |
        v
Pinecone: hospice-index
        |
        v
Semantic Search
```

`VectorStore` initializes the Pinecone client, accesses the index,
queries vectors, retrieves metadata, and returns similarity scores.

## 6. OpenAI Embeddings

An `EmbeddingService` converts provider text and user queries into
numerical embedding vectors.

``` text
Query
  |
  v
EmbeddingService
  |
  v
Query Vector
  |
  v
Pinecone
```

This enables semantic rather than exact-keyword search.

## 7. Semantic Search and Metadata Filtering

`HospiceService.semantic_search()` combines embeddings with Pinecone
vector retrieval.

Metadata filtering was added for values including:

``` text
state
ownership / proprietary_nonprofit
```

Example:

``` text
Query: community hospice provider
State: TX
Ownership: N
```

This combines semantic relevance with deterministic structured
constraints.

## 8. Manual RAG

The first RAG implementation was intentionally built manually.

``` text
Question
   |
   v
Semantic Search
   |
   v
Pinecone
   |
   v
Relevant Providers
   |
   v
Context Construction
   |
   v
OpenAI
   |
   v
Answer + Sources
```

The manual RAG implementation retrieves relevant providers, applies a
relevance threshold, builds context, calls the LLM, and returns the
generated answer together with source records.

Grounding rules prevent unsupported provider-quality claims,
interpretation of vector similarity as healthcare quality, invented
clinical recommendations, and patient-specific medical advice.

## 9. LangChain RAG

After understanding manual RAG, a LangChain implementation was added.

The project can therefore support:

``` text
AIService
├── ManualRagService
├── LangChainRagService
└── HospiceGraph
```

Modes used by the API include:

``` text
manual
langchain
langgraph
```

This makes it possible to compare manual orchestration with
framework-based orchestration.

## 10. AIService

`AIService` acts as the central AI orchestration layer between FastAPI
and the available implementations.

``` text
POST /api/ai/ask
       |
       v
    AIService
       |
       +--> Manual RAG
       +--> LangChain RAG
       +--> LangGraph
```

This prevents framework-specific logic from leaking into API routes.

## 11. LangGraph

LangGraph was introduced to route different user intents to specialized
workflows.

Current graph:

``` text
START
  |
  v
ContextNode
  |
  v
HospiceRouter
  |
  +----------------+----------------+----------------+----------------+
  |                |                |                |
  v                v                v                v
ProviderSearch   Comparison      Analytics       GeneralInfo
  |                |                |                |
  +----------------+----------------+----------------+
                                   |
                                   v
                                  END
```

## 12. LangGraph State

`HospiceGraphState` maintains shared graph state.

Important values include:

``` text
messages
question
resolved_question
state_filter
ownership
top_k
intent
results
answer
sources
```

`messages` uses LangGraph's `add_messages` reducer so conversation
messages accumulate across turns.

## 13. Intent Routing

`HospiceRouter` uses an LLM to classify requests.

Current intents:

``` text
provider_search
comparison
analytics
general_info
```

Examples:

``` text
Find nonprofit hospices in Texas
-> provider_search

Compare the first two
-> comparison

How many hospice providers are there?
-> analytics

What is hospice care?
-> general_info
```

The router uses `resolved_question` when available.

## 14. ProviderSearchNode

`ProviderSearchNode`:

-   Uses the resolved conversational question.
-   Calls `LangChainRagService`.
-   Uses remembered state/ownership filters.
-   Returns answer and sources.
-   Saves sources into `results`.
-   Adds the assistant answer to conversation messages.

Saving `results` allows later turns to refer to previously retrieved
providers.

## 15. AnalyticsNode

`AnalyticsNode` handles numerical questions using `AnalyticsService`.

The LLM is used to express calculated analytics naturally, while the
numbers themselves come from structured dataset processing.

The node also uses `resolved_question` and stores its assistant response
in message history.

## 16. GeneralInfoNode

`GeneralInfoNode` handles general hospice-care questions that do not
require provider retrieval.

It uses the resolved conversational question, generates a general
informational response, avoids patient-specific diagnosis/treatment
advice, and saves its response into message history.

## 17. LangGraph Conversation Memory

Conversation memory was added using:

``` python
InMemorySaver
```

Each conversation receives a `thread_id`.

Example:

``` text
conversation-101
```

The same thread can support:

``` text
Turn 1:
Find nonprofit hospice providers in Texas.

Turn 2:
Now focus on Dallas.

Turn 3:
Compare the first two.
```

`InMemorySaver` only survives while the current application process
remains alive. Uvicorn reloads/restarts clear this memory, so persistent
checkpoint storage remains a future production improvement.

## 18. ContextNode

A `ContextNode` was placed before the router to make stored memory
useful.

It considers:

-   Previous user/assistant messages.
-   Previous provider results.
-   The latest user question.

Example:

``` text
Previous:
Find nonprofit hospices in Texas.

Latest:
Now focus on Dallas.

Resolved:
Find nonprofit hospice providers in Dallas, Texas.
```

It can also resolve references such as:

``` text
the first two
the second provider
those providers
them
the previous results
```

This transformed checkpoint storage into practical conversational
context.

## 19. Filter Preservation

Graph input construction was changed so missing request parameters do
not overwrite remembered values with `None`.

For example:

``` text
Turn 1:
state = TX
ownership = N

Turn 2:
"Now focus on Dallas."
```

The second request can retain the relevant Texas/nonprofit context
rather than clearing it.

## 20. ComparisonNode

A specialized comparison workflow was added instead of treating
comparison as another semantic-search request.

``` text
Previous Search
      |
      v
Saved Results
      |
      v
Compare the first two
      |
      v
ContextNode
      |
      v
Router -> comparison
      |
      v
ComparisonNode
```

The comparison uses available metadata such as organization name,
business name, location, ownership, NPI, and CCN.

It does not treat similarity score as provider quality or claim
unsupported clinical superiority.

## 21. LangSmith

LangSmith tracing and observability were configured and verified.

It provides visibility into:

-   RAG calls.
-   LangGraph execution.
-   Context resolution.
-   Intent routing.
-   LLM calls.
-   Specialized node execution.

Named runs/tags include concepts such as:

``` text
hospice_context_resolver
hospice_intent_router
hospice_langgraph_memory
hospice_provider_comparison
```

## 22. Important Problems Solved

Practical development issues resolved include:

-   `ModuleNotFoundError` for the Hugging Face `datasets` package.
-   CSV/Unicode/schema inference issues.
-   `DatasetDict` not supporting Pandas `.head()`.
-   JSON serialization errors caused by `NaN`.
-   Missing Pinecone imports.
-   Missing `VectorStore.semantic_search()`.
-   Python indentation errors.
-   Duplicate Pydantic `AskRequest` definitions removing `mode`.
-   Incorrect function-call syntax for `thread_id`.
-   LangGraph checkpointer initialization order.
-   Conversation memory initially storing state without effectively
    using context.
-   Preserving filters and previous results across follow-up turns.

## 23. Deliberately Skipped / Postponed

The following were discussed but intentionally not added at this stage:

-   PostgreSQL for the retrieval layer.
-   Dedicated recommendation workflow.
-   MCP integration.

## 24. Current Technology Stack

### API

-   Python
-   FastAPI
-   Uvicorn
-   Pydantic

### Data

-   HHS hospice enrollment dataset
-   Hugging Face `datasets`
-   Pandas

### AI

-   OpenAI
-   OpenAI embeddings
-   GPT-4.1-mini in implemented LLM flows

### Vector Database

-   Pinecone

### Frameworks

-   LangChain
-   LangGraph

### Observability

-   LangSmith

## 25. AI Engineering Capabilities Implemented

``` text
Dataset acquisition/loading        DONE
Data cleanup/API-safe conversion   DONE
FastAPI service layer              DONE
Structured analytics               DONE
Embeddings                         DONE
Pinecone vector database           DONE
Semantic search                    DONE
Metadata filtering                 DONE
Manual RAG                         DONE
LangChain RAG                      DONE
LangGraph                          DONE
Intent routing                     DONE
Conversation memory                DONE
Context resolution                 DONE
Comparison workflow                DONE
LangSmith tracing                  DONE

Evaluation                         NEXT / PLANNED
Persistent memory                  FUTURE
More agentic capabilities          FUTURE
MCP                                FUTURE
Deployment / LLMOps                FUTURE


## 26. Recommended Next Phase

The next high-value phase is evaluation rather than immediately adding
more frameworks.

Areas to evaluate:

1.  Retrieval relevance.
2.  Answer groundedness.
3.  Hallucination rate.
4.  Routing accuracy.
5.  Memory/context accuracy.
6.  Comparison accuracy.
7.  Latency.
8.  Token/cost usage.
9.  Failure handling.

Potential structure:

``` text
evals/
├── datasets/
│   └── hospice_eval_cases.py
├── evaluators/
│   ├── retrieval_evaluator.py
│   ├── groundedness_evaluator.py
│   └── routing_evaluator.py
└── run_evals.py
```

## Overall Status

The project has evolved beyond a basic RAG demo.

``` text
Hospice Dataset
      |
      v
Semantic Retrieval
      |
      v
Grounded Manual RAG
      |
      v
LangChain RAG
      |
      v
LangGraph Orchestration
      |
      v
Conversational Memory
      |
      v
Context-Aware Specialized Workflows
      |
      v
LangSmith Observability
      |
      v
Evaluation / Production Hardening
```

The current project is a strong foundation for continuing into
evaluation, persistent memory, more advanced agentic workflows,
deployment, and LLMOps.
