# src/parser/core.py



# Imports
from tree_sitter import Language, Parser
import tree_sitter_python as tspython
import tree_sitter_java as tsjava

class ParserEngine:
    '''
    Core parsing enginge for SentinelPR.
    Responsible for transforming src code into a CST.
    '''

    # Map supported language for their tree sitter grammers
    def __init__(self):
        self.languages: dict[str, Language] = {
            "python": Language(tspython.language()),
            "java": Language(tsjava.language())
        }

        # Initialize internal parser
        self._parser = Parser()
    
    def parse(self, language_id: str, source_code: str):
        '''
        Parse src code into CST based on language.
        
        Args:
            - language_id: represents the key for the language in self.languages
            - source_code: the actual raw code of string to be parsed

        This returns a tree sitter Tree object representing the CST
        '''

        if language_id not in self.languages:
            raise ValueError(f"{language_id} is not a supported.")

        # Set the parsers active language
        self._parser.language = self.languages[language_id]
        return self._parser.parse(bytes(source_code, "utf-8"))