import math
import pandas as pd

from app.services.dataset_service import DatasetService
from app.utils.text import hospice_to_text
from app.ai.embeddings.embedding_service import EmbeddingService
from app.ai.vectorstore.vector_store import VectorStore


BATCH_SIZE = 100


def clean_value(value):

    if pd.isna(value):
        return ""

    return str(value)


def main():

    dataset_service = DatasetService()
    embedding_service = EmbeddingService()
    vector_store = VectorStore()

    df = dataset_service.load_hospice_dataset()

    total_records = len(df)

    print(f"Total records: {total_records}")

    total_batches = math.ceil(
        total_records / BATCH_SIZE
    )

    for batch_number, start in enumerate(
        range(0, total_records, BATCH_SIZE),
        start=1
    ):

        end = min(
            start + BATCH_SIZE,
            total_records
        )

        batch_df = df.iloc[start:end]

        texts = []

        metadata_list = []

        ids = []

        for index, row in batch_df.iterrows():

            text = hospice_to_text(row)

            texts.append(text)

            ids.append(
                f"hospice-{index}"
            )

            metadata_list.append(
                {
                    "organization_name": clean_value(
                        row.get("organization_name")
                    ),

                    "doing_business_as_name": clean_value(
                        row.get("doing_business_as_name")
                    ),

                    "provider_type_text": clean_value(
                        row.get("provider_type_text")
                    ),

                    "organization_type_structure": clean_value(
                        row.get(
                            "organization_type_structure"
                        )
                    ),

                    "proprietary_nonprofit": clean_value(
                        row.get("proprietary_nonprofit")
                    ),

                    "city": clean_value(
                        row.get("city")
                    ),

                    "state": clean_value(
                        row.get("state")
                    ),

                    "zip_code": clean_value(
                        row.get("zip_code")
                    ),

                    "npi": clean_value(
                        row.get("npi")
                    ),

                    "ccn": clean_value(
                        row.get("ccn")
                    ),

                    "text": text
                }
            )

        print(
            f"Generating embeddings "
            f"for batch {batch_number}/{total_batches}"
        )

        embeddings = (
            embedding_service
            .generate_embeddings(texts)
        )

        vectors = []

        for i in range(len(embeddings)):

            vectors.append(
                {
                    "id": ids[i],
                    "values": embeddings[i],
                    "metadata": metadata_list[i]
                }
            )

        vector_store.upsert(vectors)

        print(
            f"Uploaded records "
            f"{start + 1} - {end}"
        )

    print("Finished indexing hospice dataset.")


if __name__ == "__main__":
    main()