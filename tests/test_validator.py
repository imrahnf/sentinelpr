import unittest
from src.validator.schema_guard import SchemaGuard

class TestSchemaGuard(unittest.TestCase):
    def test_filter_hallucinations(self):
        # We claim only 'main.py' changed
        changed_files = {"src/main.py"}
        symbol_map = {} # Unused
        
        guard = SchemaGuard(changed_files, symbol_map)
        
        # Input: Mixed bag of valid and invalid reviews
        raw_reviews = [
            # Valid
            {"file_path": "src/main.py", "line": 10, "issue": "Bug", "severity": "HIGH"},
            # Invalid (File not in PR)
            {"file_path": "src/ghost.py", "line": 5, "issue": "Bug", "severity": "LOW"},
            # Invalid (Line is 0)
            {"file_path": "src/main.py", "line": 0, "issue": "Bug", "severity": "LOW"}
        ]
        
        clean_reviews = guard.validate_reviews(raw_reviews)
        self.assertEqual(len(clean_reviews), 1)
        self.assertEqual(clean_reviews[0]['file_path'], "src/main.py")

if __name__ == '__main__':
    unittest.main()