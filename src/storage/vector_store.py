import os
import chromadb
from chromadb.config import Settings

class VectorStore:
    def __init__(self, persist_dir: str = ".sentinel/db"):
        self.client = chromadb.PersistentClient(path=persist_dir) 
        self.collection = self.client.get_or_create_collection(name="sentinel_symbols")

    def upsert(self, ids: list[str], vectors: list[list[float]], metadata: list[dict]):
        self.collection.upsert(
            ids=ids,
            embeddings=vectors,
            metadatas=metadata,
            documents=[m['snippet'] for m in metadata]
        )

    def get_symbols_for_file(self, file_path: str):
        result = self.collection.get(
            where={"file_path": file_path},
            include=["metadatas"]
        )
        
        symbols = []
        if result['ids'] and result['metadatas']:
            for id, meta in zip(result['ids'], result['metadatas']):
                meta['id'] = id
                symbols.append(meta)
                
        return symbols

    def search(self, query_vector: list, limit: int = 5):
        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=limit,
            include=["metadatas", "documents", "distances"]
        )
        
        matches = []
        if results['ids']:
            for i in range(len(results['ids'][0])):
                match_data = results['metadatas'][0][i]
                
                match_data['id'] = results['ids'][0][i]
                match_data['snippet'] = results['documents'][0][i]
                match_data['distance'] = results['distances'][0][i]
                
                matches.append(match_data)
        return matches

    def delete(self, file_path: str):
        self.collection.delete(
            where={"file_path": file_path}
        )