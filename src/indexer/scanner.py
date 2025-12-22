# src/indexer/scanner.py
import json
import os
from .hasher import calculate_hash

class Scanner:
    def __init__(self, state_path: str = ".sentinel/hashes.json"):
        self.state_path = state_path
        self.state = self._load_state()

    def _load_state(self) -> dict:
        try:
            with open(self.state_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            print("JSON file not found.")
            return {}

    def scan(self, directory: str) -> list[str]:
        ignored_dirs = {".venv", "venv", "__pycache__", "__init__", ".git", ".sentinel", "node_modules"}
        supported_exts = {".py", ".java"}
        ignored_files = {"__init__.py"}

        # Returns a list of file paths that have changed or are new
        changed_files = []
        seen_files = set() # Track files currently on disk

        for (root,dirs,files) in os.walk(directory, topdown=True):
            # Modify dirs so that it ignores things that should never be indexed
            dirs[:] = [d for d in dirs if d not in ignored_dirs]

            for file in files:
                if file in ignored_files:
                    continue

                # Only check for target languages
                ext = os.path.splitext(file)[1]
                if ext in supported_exts:
                    full_path = os.path.normpath(os.path.join(root, file))
                    seen_files.add(full_path)

                    hash = calculate_hash(full_path)

                    # Since the hash changed, we can add it to the list of changed_files
                    if hash!= self.state.get(full_path):
                        changed_files.append(full_path)

        # Deletion cleanup- remove files from state if they do not exist
        deleted_files = set(self.state.keys()) - seen_files
        for path in deleted_files:
            del self.state[path]

        return changed_files

    def update_state(self, file_path: str, new_hash: str):
        # Update in memory dict & ensure it actually exists
        self.state[file_path] = new_hash
        os.makedirs(os.path.dirname(self.state_path), exist_ok=True)

        # Write back to the JSON file
        with open(self.state_path, 'w') as f:
            json.dump(self.state, f, indent=4)