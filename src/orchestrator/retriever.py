from typing import List, Dict
from src.ai.embedder import Embedder
from src.storage.vector_store import VectorStore

class ContextRetriever:
    def __init__(self, vector_store: VectorStore, embedder: Embedder):
        self.store = vector_store
        self.embedder = embedder

    def retrieve_context(self, symbol: Dict, limit: int = 3) -> List[Dict]:
        snippet = symbol.get("snippet")
        if not snippet:
            return []

        # Embed the modified code
        vectors = self.embedder.embed_batch([snippet])
        if not vectors:
            return []
        
        # earch DB
        # We ask for limit + 1 because the top result is usually the function itself
        results = self.store.search(vectors[0], limit=limit + 1)
        
        # ilter out self
        context_snippets = []
        for res in results:
            if res.get("id") == symbol.get("id"):
                continue
            context_snippets.append(res)
            
        return context_snippets[:limit]