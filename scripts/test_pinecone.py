from app.services.dataset_service import DatasetService
from app.utils.text import hospice_to_text
from app.ai.embeddings.embedding_service import EmbeddingService
from app.ai.vectorstore.vector_store import VectorStore


dataset_service = DatasetService()
embedding_service = EmbeddingService()
vector_store = VectorStore()

vector_store.create_index()

index = vector_store.get_index()

df = dataset_service.load_hospice_dataset()



vectors = []

for i in range(5):

    row = df.iloc[i]

    text = hospice_to_text(row)

    embedding = embedding_service.generate_embedding(text)

    vectors.append(
        {
            "id": f"hospice-{i}",
            "values": embedding,
            "metadata": {
                "organization_name": str(
                    row.get("organization_name", "")
                ),
                "city": str(
                    row.get("city", "")
                ),
                "state": str(
                    row.get("state", "")
                ),
                "npi": str(
                    row.get("npi", "")
                ),
                "proprietary_nonprofit": str(
                    row.get("proprietary_nonprofit", "")
                ),
                "text": text
            }
        }
    )

index.upsert(
    vectors=vectors
)

print("Uploaded 5 hospice vectors")



query = "nonprofit hospice care provider"

query_embedding = embedding_service.generate_embedding(query)

results = index.query(
    vector=query_embedding,
    top_k=3,
    include_metadata=True
)

print(results)