import unittest
from unittest.mock import MagicMock
from src.models.diffhunk import DiffHunk
from src.orchestrator.mapper import Mapper
from src.storage.vector_store import VectorStore

class TestMapper(unittest.TestCase):
    def test_map_hits_correctly(self):
        # 1. Mock the VectorStore (Don't use real DB)
        mock_store = MagicMock(spec=VectorStore)
        
        # Setup the fake return data (The "Bucket")
        mock_store.get_symbols_for_file.return_value = [
            {
                "id": "src/main.py::main",
                "symbol_name": "main",
                "start_line": 10,
                "end_line": 20,
                "file_path": "src/main.py"
            }
        ]

        mapper = Mapper(mock_store)

        # 2. Define the Input (The "Ball" - Line 15 is inside 10-20)
        hunk = DiffHunk(
            file_path="src/main.py",
            start_line=14,
            changed_lines=[15] 
        )

        # 3. Run Logic
        result = mapper.map_diffs_to_symbols([hunk])

        # 4. Verify
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['symbol_name'], 'main')
    
    def test_map_misses_correctly(self):
        # 1. Mock Store
        mock_store = MagicMock(spec=VectorStore)
        mock_store.get_symbols_for_file.return_value = [
            {
                "id": "src/main.py::main",
                "symbol_name": "main",
                "start_line": 10,
                "end_line": 20, # Function ends at 20
                "file_path": "src/main.py"
            }
        ]
        mapper = Mapper(mock_store)

        # 2. Input (Line 25 is OUTSIDE the function)
        hunk = DiffHunk(
            file_path="src/main.py",
            start_line=25,
            changed_lines=[25] 
        )

        # 3. Run
        result = mapper.map_diffs_to_symbols([hunk])

        # 4. Verify
        self.assertEqual(len(result), 0)

if __name__ == '__main__':
    unittest.main()