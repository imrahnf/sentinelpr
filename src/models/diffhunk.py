# src/models/diffhunk.py
from dataclasses import dataclass
from typing import List

@dataclass
class DiffHunk:
    file_path: str
    start_line: int
    changed_lines: List[int] # line numbers that were added/modified