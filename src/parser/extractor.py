# src.parser.extractor.py
from src.models.symbol import Symbol

class SymbolExtractor:
    def __init__(self, source_code: str):
        # We need src code as bytes to slice out names of functions
        self.source_bytes = bytes(source_code, "utf-8")

        # Map raw CST types to Symbol types
        self.target_types = {
            "function_definition": "function", # Python
            "class_definition": "class",       # Python
            "method_declaration": "function",  # Java
            "class_declaration": "class"       # Java
        }

    def extract(self, node, file_path: str) -> list[Symbol]:
        symbols = []

        # Process current node
        if node.type in self.target_types:
            # Get node's name and slice the source bytes by start and end bytes of the name_node we got
            name_node = node.child_by_field_name("name")
            name_text = self.source_bytes[name_node.start_byte:name_node.end_byte].decode("utf-8") if name_node else "anonymous"

            # Get the full content of the symbol body
            symbol_content = self.source_bytes[node.start_byte:node.end_byte].decode("utf-8")

            # Create Symbol object and append to symbols
            symbols.append(Symbol(
                name=name_text, 
                type=self.target_types[node.type], # Clean map name
                content=symbol_content,
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                file_path=file_path
            ))
        
        # Recursively call for each child to ensure we find methods inside classes
        for child in node.children:
            child_symbols = self.extract(child, file_path)
            symbols.extend(child_symbols)
        
        return symbols