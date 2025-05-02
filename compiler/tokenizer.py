import re
from utils.errors import TokenizationError
import logging

logger = logging.getLogger(__name__)

patterns = [
    (r"\bSELECT\b", "KEYWORD"),
    (r"\bFROM\b", "KEYWORD"),
    (r"\bINSERT\b", "KEYWORD"),
    (r"\bINTO\b", "KEYWORD"),
    (r"\bVALUES\b", "KEYWORD"),
    (r"[a-zA-Z_][a-zA-Z0-9_]*", "IDENTIFIER"),
    (r"\*", "ASTERISK"),
    (r",", "COMMA"),
    (r"\(", "LPAREN"),
    (r"\)", "RPAREN"),
    (r"'", "QUOTE"),
    (r"[0-9]+", "NUMBER"),
    (r"\s+", None),  # Skip whitespace
]

class Tokenizer:
    def tokenize(self, sql):
        sql = sql.strip() # remove trailing whitespaces
        tokens = []
        i = 0

        while i < len(sql):
            match_found = False
            for pattern, token_type in patterns:
                regex = re.compile(pattern, re.IGNORECASE)
                match = regex.match(sql, i)  # Match from full string at index i
                if match:
                    match_text = match.group(0)
                    if token_type:
                        tokens.append((token_type, match_text.upper()))
                    i = match.end() 
                    match_found = True
                    break
            if not match_found:
                raise TokenizationError(f"Unknown token at: '{sql[i:]}'")

        logger.info(f"Tokenized SQL: {tokens}")
        return tokens
