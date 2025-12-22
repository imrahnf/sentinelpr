# src/main.py
import os

from src.indexer.scanner import Scanner
from src.parser.core import ParserEngine
from src.parser.extractor import SymbolExtractor
from src.indexer.hasher import calculate_hash

def main():
    LANG_MAP = {
        ".py": "python", 
        ".java": "java"
    }

    scanner = Scanner()
    parser = ParserEngine()
    
    print("Scanning for changes...")
    changed_files = scanner.scan(".")
    
    if not changed_files:
        print("No files changed. Skipping index.")
        return

    print(f"Found {len(changed_files)} files to process.")

    for file_path in changed_files:
        try:
            # Determine language from extension
            ext = os.path.splitext(file_path)[1]
            lang = LANG_MAP.get(ext)

            with open(file_path, 'r') as f:
                code = f.read()
            
            # Parse tree
            tree = parser.parse(lang, code)
            extractor = SymbolExtractor(code)
            symbols = extractor.extract(tree.root_node, file_path)
            
            # Save new hash only if the parsing succeeded
            new_hash = calculate_hash(file_path)
            scanner.update_state(file_path, new_hash)
            
            print(f"Successfully extracted {len(symbols)} symbols.")
        except Exception as e:
            print(f"Failed to index {file_path}: {e}")
            continue # Move onto the next file

if __name__ == "__main__":
    main()