# src.models.symbol.py

from dataclasses import dataclass

@dataclass
class Symbol:
    name: str
    type: str # 'function' or 'class'
    content: str
    start_line: int
    end_line: int
    file_path: str