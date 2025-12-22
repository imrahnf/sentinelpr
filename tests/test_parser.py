import sys
import os
import unittest

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.parser.core import ParserEngine
from src.parser.extractor import SymbolExtractor

class TestParser(unittest.TestCase):
    def setUp(self):
        """Runs before every test. Setup the parser."""
        self.parser = ParserEngine()  # No language param

    def test_parse_simple_function(self):
        """Test if we can extract a simple function."""
        code = """
def hello_world():
    print("Hello")
    return True
"""
        # Parse the raw string
        tree = self.parser.parse("python", code)  # Use parse(language, code)
        
        # Extract symbols
        self.extractor = SymbolExtractor(code)  # Pass code to extractor
        symbols = self.extractor.extract(tree.root_node, "test_file.py")  # Use tree.root_node
        
        # Assertions
        self.assertEqual(len(symbols), 1)
        self.assertEqual(symbols[0].name, "hello_world")
        self.assertEqual(symbols[0].type, "function")

if __name__ == "__main__":
    unittest.main()