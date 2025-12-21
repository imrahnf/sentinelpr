# src/parser/test_extractor.py
from .core import ParserEngine
from .extractor import SymbolExtractor

def test_extraction():
    engine = ParserEngine()
    code = """
class MyClass:
    def method_one(self):
        pass

def top_level_func():
    pass
    """
    
    # 1. Parse
    tree = engine.parse("python", code)
    
    # 2. Extract
    extractor = SymbolExtractor(code)
    symbols = extractor.extract(tree.root_node, "test.py")
    
    # 3. Print results
    for s in symbols:
        print(f"Found {s.type}: {s.name} (Lines {s.start_line}-{s.end_line})")

if __name__ == "__main__":
    test_extraction()