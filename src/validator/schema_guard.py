from typing import List, Dict, Set

class SchemaGuard:
    def __init__(self, changed_files: Set[str], symbol_map: Dict[str, Dict]):
        self.changed_files = changed_files
        self.symbol_map = symbol_map

    def validate_reviews(self, reviews: List[Dict]) -> List[Dict]:
        valid_reviews = []
        
        for review in reviews:
            # heck for missing keys
            if not all(k in review for k in ["file_path", "line", "issue"]):
                print(f"Dropped malformed review: {review}")
                continue

            path = review['file_path']
            line = review['line']

            # Check if file is part of the PR
            if path not in self.changed_files:
                print(f"Dropped review for untouched file: {path}")
                continue

            # SLine number must be positive
            if not isinstance(line, int) or line < 1:
                print(f"Dropped invalid line number: {line} in {path}")
                continue

            valid_reviews.append(review)
            
        return valid_reviews