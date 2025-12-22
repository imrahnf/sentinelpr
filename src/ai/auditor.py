import os
import json
import google.generativeai as genai
from typing import List, Dict
from src.ai.prompts import AUDITOR_SYSTEM_PROMPT, AUDITOR_USER_TEMPLATE

class Auditor:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-flash-latest')

    def analyze(self, diff_text: str, affected_symbol: Dict, context_snippets: List[Dict]) -> List[Dict]:
        # repare the Context String (Flatten the RAG results)
        context_str = "\n".join([
            f"--- Snippet from {c['file_path']} ---\n{c['snippet']}" 
            for c in context_snippets
        ])

        # Format the Prompt
        prompt = AUDITOR_USER_TEMPLATE.format(
            context_str=context_str if context_str else "No relevant context found.",
            symbol_code=affected_symbol.get('snippet', 'Code not found'),
            diff_text=diff_text
        )

        # Call Gemini
        try:
            response = self.model.generate_content(
                contents=[
                    {"role": "user", "parts": [AUDITOR_SYSTEM_PROMPT, prompt]}
                ],
                generation_config={"response_mime_type": "application/json"}
            )
            
            # Parse JSON
            result = json.loads(response.text)
            reviews = result.get("reviews", [])
            
            # Add file_path to each review
            for review in reviews:
                review['file_path'] = affected_symbol['file_path']
            
            return reviews

        except json.JSONDecodeError:
            print("Auditor produced invalid JSON.")
            return []
        except Exception as e:
            print(f"AI Error: {e}")
            return []