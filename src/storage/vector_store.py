import chromadb
from chromadb.config import Settings
import os


class VectorStore:
    def __init__(self, persist_dir: str = ".sentinel/db"):
        self.client = chromadb.PersistentClient(path=persist_dir) 
        self.collection = self.client.get_or_create_collection(name="sentinel_symbols")

    def upsert(self, ids: list[str], vectors: list[list[float]], metadata: list[dict]):
        self.collection.upsert(
            ids=ids,
            embeddings=vectors,
            metadatas=metadata
        )

    def delete(self, file_path: str):
        self.collection.delete(
            where={"file_path": file_path}
        )

    def query(self, query_vector: list[float], limit: int = 5):
        return self.collection.query(
            query_embeddings=[query_vector], 
            n_results=limit
        )