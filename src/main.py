# src/main.py
import os
import sys

# --- Imports ---
from src.indexer.scanner import Scanner
from src.parser.core import ParserEngine
from src.parser.extractor import SymbolExtractor
from src.indexer.hasher import calculate_hash

# Milestone 2 Imports (The New Brain)
from src.indexer.persistence import verify_db_integrity, reset_db
from src.storage.vector_store import VectorStore
from src.ai.embedder import Embedder

def main():
    print("---|| SentinelPR Indexer Started ||---")

    if not verify_db_integrity(".sentinel/db"):
        reset_db(".sentinel/db")

    LANG_MAP = {
        ".py": "python", 
        ".java": "java"
    }

    # Initialize the components
    scanner = Scanner()
    parser = ParserEngine()
    store = VectorStore()
    embedder = Embedder()
    
    print("Scanning for changes...")
    changed_files = scanner.scan(".")
    
    if not changed_files:
        print("No files changed. Skipping index.")
        return

    print(f"Found {len(changed_files)} files to process.")

    for file_path in changed_files:
        try:
            # Filter by language
            ext = os.path.splitext(file_path)[1]
            lang = LANG_MAP.get(ext)
            if not lang:
                continue

            with open(file_path, 'r') as f:
                code = f.read()
            
            # Parse tree
            tree = parser.parse(lang, code)
            extractor = SymbolExtractor(code)
            symbols = extractor.extract(tree.root_node, file_path)

            # If file is valid but empty, it is still processed
            if not symbols:
                new_hash = calculate_hash(file_path)
                scanner.update_state(file_path, new_hash)
                continue
            
            # symbols is a list of Symbols
            snippets = [s.content for s in symbols]

            print(f"Generating embeddings for {file_path}")
            vectors = embedder.embed_batch(snippets)

            # Prepare metadata
            ids = []
            metadata = []

            for sym, vec in zip(symbols, vectors):
                uid = f"{sym.file_path}::{sym.name}"
                ids.append(uid)

                metadata.append({
                    "file_path": sym.file_path,
                    "symbol_name": sym.name,
                    "type": sym.type,
                    "start_line": sym.start_line,
                    "end_line": sym.end_line,
                    "snippet": sym.content
                })

            store.upsert(ids=ids, vectors=vectors, metadata=metadata)
            print(f"Indexed {len(symbols)} symbols for {file_path}")
            
            new_hash = calculate_hash(file_path)
            scanner.update_state(file_path, new_hash)

        except Exception as e:
            print(f"Failed to index {file_path}: {e}")
            continue # Move onto the next file
    print("---|| SentinelPR Indexer Complete ||---")

if __name__ == "__main__":
    main()