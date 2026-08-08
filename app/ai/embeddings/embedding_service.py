import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class EmbeddingService:

    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )

        self.model = "text-embedding-3-small"

    def generate_embedding(self, text: str) -> list[float]:
        response = self.client.embeddings.create(
            model=self.model,
            input=text
        )

        return response.data[0].embedding

    def generate_embeddings(
        self,
        texts: list[str]
    ) -> list[list[float]]:

        response = self.client.embeddings.create(
            model=self.model,
            input=texts
        )

        return [
            item.embedding
            for item in response.data
        ]