# src.parser.test.py
from .core import ParserEngine

def verify_parser():
    engine = ParserEngine()

    # Test case : Python
    py_code = "def hello(): pass"
    py_tree = engine.parse("python", py_code)

    print(f"Python Root Node: {py_tree.root_node.type}")
    assert py_tree.root_node.type == "module"

    # Test case : Java
    java_code = "class Test { public void main() {} }"
    Java_tree = engine.parse("java", java_code)

    print(f"Java Root Node: {Java_tree.root_node.type}")
    assert Java_tree.root_node.type == "program"

if __name__ == "__main__":
    verify_parser()