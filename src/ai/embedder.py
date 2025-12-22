import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class Embedder:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        genai.configure(api_key=self.api_key)

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        try:
            # task_type="retrieval_document" optimizes vectors for storage/search
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=texts,
                task_type="retrieval_document"
            )
            
            # Return list of vectors
            return result['embedding']

        except Exception as e:
            print(f"Error generating embeddings: {e}")
            return []