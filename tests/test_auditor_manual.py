# tests/test_auditor_manual.py
import os
from dotenv import load_dotenv
from src.ai.auditor import Auditor

# Load env for API Key
load_dotenv()

def test_auditor():
    auditor = Auditor()
    
    # 1. Mock Data
    fake_diff = """
    + def calculate_total(price, tax):
    +     return price * tax  # Bug: Should be price * (1 + tax)
    """
    
    fake_symbol = {
        "snippet": "def calculate_total(price, tax):\n    return price * tax",
        "file_path": "src/utils.py"
    }
    
    fake_context = [] # No RAG
    reviews = auditor.analyze(fake_diff, fake_symbol, fake_context)
    
    print("\n--- AI REVIEWS ---")
    print(reviews)

if __name__ == "__main__":
    test_auditor()