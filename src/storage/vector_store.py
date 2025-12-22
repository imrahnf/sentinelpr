import os
import chromadb
from typing import List

from chromadb.config import Settings
from src.models.symbol import Symbol

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

    def get_symbols_for_file(self, file_path: str):
        result = self.collection.get(
            where={"file_path":file_path}
        )
        symbols = []
        if result["ids"] and result["metadatas"]:
            for id, meta in zip(result["ids"], result["metadatas"]):
                meta["id"] = id
                symbols.append(meta)
        return symbols

    def delete(self, file_path: str):
        self.collection.delete(
            where={"file_path": file_path}
        )

    def query(self, query_vector: list[float], limit: int = 5):
        return self.collection.query(
            query_embeddings=[query_vector], 
            n_results=limit
        )