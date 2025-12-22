from typing import List, Dict
from src.models.diffhunk import DiffHunk
from src.storage.vector_store import VectorStore

class Mapper:
    def __init__(self, vector_store: VectorStore):
        self.store = vector_store

    def map_diffs_to_symbols(self, hunks: List[DiffHunk]) -> List[Dict]:
        affected_symbols = []
        processed_ids = set() # To avoid duplicates

        for hunk in hunks:
            # Returns a list of dicts
            symbols = self.store.get_symbols_for_file(hunk.file_path)
            
            for sym in symbols:
                start = int(sym['start_line'])
                end = int(sym['end_line'])

                # Check if any falls within the range
                hit =  any(start <= line <= end for line in hunk.changed_lines)
                if hit:
                    if sym["id"] not in processed_ids:
                        processed_ids.add(sym["id"])
                        affected_symbols.append(sym)
                        print(f"Match found: {sym['symbol_name']}")
        return affected_symbols