import os
import sys
import argparse
import traceback
import json

# --- Core Modules ---
from src.indexer.scanner import Scanner
from src.parser.core import ParserEngine
from src.parser.extractor import SymbolExtractor
from src.indexer.hasher import calculate_hash
from src.indexer.persistence import verify_db_integrity, reset_db
from src.storage.vector_store import VectorStore
from src.ai.embedder import Embedder

# --- Audit Modules ---
from src.git.diff_parser import DiffParser
from src.orchestrator.mapper import Mapper
from src.orchestrator.retriever import ContextRetriever
from src.ai.auditor import Auditor
from src.github.commenter import PRCommenter
from src.validator.schema_guard import SchemaGuard

def run_indexer():
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
                scanner.update_state(file_path, calculate_hash(file_path))
                continue
            
            # Snippets to directly map content
            snippets = [s.content for s in symbols]
            vectors = embedder.embed_batch(snippets)

            # Prepare metadata
            ids = []
            metadata = []
            for sym, vec in zip(symbols, vectors):
                uid = f"{sym.file_path}::{sym.name}"
                ids.append(uid)

                metadata.append({
                    "id": uid,
                    "file_path": sym.file_path,
                    "symbol_name": sym.name,
                    "type": sym.type,
                    "start_line": sym.start_line,
                    "end_line": sym.end_line,
                    "snippet": sym.content
                })

            store.upsert(ids=ids, vectors=vectors, metadata=metadata)
            scanner.update_state(file_path, calculate_hash(file_path))
            print(f"Indexed {file_path}")

        except Exception as e:
            print(f"Failed to index {file_path}: {e}")
            continue # Move onto the next file
    print("---|| SentinelPR Indexer Complete ||---")

def run_auditor(diff_path: str, repo: str = None, pr: int = None, token: str = None):
    print("---|| SentinelPR Auditor Started ||---")
    try:
        # Read the Diff
        with open(diff_path, 'r') as f:
            diff_text = f.read()

        # nit Components
        store = VectorStore()
        embedder = Embedder()
        parser = DiffParser()
        mapper = Mapper(store)
        retriever = ContextRetriever(store, embedder)
        auditor = Auditor()

        # Parse & Map
        print("Parsing Diff...")
        hunks = parser.parse(diff_text)
        affected_symbols = mapper.map_diffs_to_symbols(hunks)

        if not affected_symbols:
            print("No symbols affected by this change.")
            return

        print(f"Found {len(affected_symbols)} affected symbols.")

        # udit Loop
        all_reviews = []
        for sym in affected_symbols:
            print(f"Auditing {sym['symbol_name']}...")
            
            # RAG
            context = retriever.retrieve_context(sym)
            
            # AI Generate Review
            reviews = auditor.analyze(diff_text, sym, context)
            all_reviews.extend(reviews)

        changed_files = {h.file_path for h in hunks}
        guard = SchemaGuard(changed_files, {}) # Empty symbol map is fine for now
        valid_reviews = guard.validate_reviews(all_reviews)

        # Post or Print
        if token and repo and pr:
            print(f"🚀 Posting {len(valid_reviews)} reviews to {repo} PR #{pr}...")
            commenter = PRCommenter(repo, pr, token)
            commenter.post_comments(valid_reviews)
        else:
            print("No issues found." if not valid_reviews else "\nDETECTED ISSUES:")
            if valid_reviews:
                print(json.dumps(valid_reviews, indent=2))

    except Exception as e:
        print(f"Audit Failure: {e}")
        traceback.print_exc()
        sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description="SentinelPR: AI Code Auditor")
    parser.add_argument("--diff", help="Path to a git diff file to audit")
    parser.add_argument("--repo", help="Full repository name (owner/repo)")
    parser.add_argument("--pr", type=int, help="Pull request number")
    parser.add_argument("--token", help="GitHub token")
    
    args = parser.parse_args()
    
    if args.diff:
        run_auditor(args.diff, args.repo, args.pr, args.token)
    else:
        run_indexer()

if __name__ == "__main__":
    main()