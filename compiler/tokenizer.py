import re
from utils.errors import TokenizationError
from utils.logger import get_logger
from compiler.tok_def import Token

logger = get_logger(__name__)

patterns = [
    (r"\bSELECT\b", "KEYWORD"),
    (r"\bFROM\b", "KEYWORD"),
    (r"\bINSERT\b", "KEYWORD"),
    (r"\bINTO\b", "KEYWORD"),
    (r"\bVALUES\b", "KEYWORD"),
    (r"\bCREATE\b", "KEYWORD"),
    (r"\bTABLE\b", "KEYWORD"),
    (r"\bDELETE\b", "KEYWORD"),
    (r"\bUPDATE\b", "KEYWORD"),
    (r"\bSET\b", "KEYWORD"),
    (r"\bDROP\b", "KEYWORD"),
    (r"\bWHERE\b", "KEYWORD"),
    
    (r"\bINT\b", "KEYWORD"),  # Added INT type as a keyword
    (r"\bTEXT\b", "KEYWORD"), # Added TEXT type as a keyword
    (r"\bREAL\b", "KEYWORD"), # Added REAL type as a keyword
    (r"\bBOOLEAN\b", "KEYWORD"), # Added BOOLEAN type as a keyword
    (r"'[^']*'", "STRING"),  # Single-quoted strings
    (r'"[^"]*"', "STRING"),  # Double-quoted strings
    (r"[a-zA-Z_][a-zA-Z0-9_]*", "IDENTIFIER"),  # Identifiers like column names or table names
    (r"\*", "ASTERISK"),
    (r",", "COMMA"),
    (r"\(", "LPAREN"),
    (r"\)", "RPAREN"),
    (r"'", "QUOTE"),
    (r"\d+\.\d+", "NUMBER"),  # Floating point numbers (e.g., 10.5)
    (r"\d+", "NUMBER"),       # Integers like 5, 100, etc.
    (r"\s+", None),           # Skip whitespace
    (r";", "SEMICOLON"), 
    (r"\.", "DOT"),
    (r"=", "EQUALS"),
    (r'"[^"]*"|\'[^\']*\'', "STRING"), # String literals
    (r"!=", "NOTEQUALS"),
    (r"<=", "LESSEQUAL"),
    (r">=", "GREATEREQUAL"),
    (r"<", "LESSTHAN"),
    (r">", "GREATERTHAN"),
    (r"=", "EQUALS"),
]

class Tokenizer:
    def tokenize(self, sql):
        sql = sql.strip()  # Remove trailing whitespaces
        tokens = []
        i = 0

        while i < len(sql):
            match_found = False
            for pattern, token_type in patterns:
                regex = re.compile(pattern, re.IGNORECASE)
                match = regex.match(sql, i) 
                if match:
                    match_text = match.group(0)
                    
                    if token_type:
                        if token_type == "KEYWORD":
                            value = match_text.upper() 
                        elif token_type == "STRING":
                            value = match_text[1:-1]
                        else:
                            value = match_text

                        token = Token(token_type=token_type, value=value, position=i)
                        tokens.append(token)

                    i = match.end() 
                    match_found = True
                    break

            if not match_found:
                error_msg = f"Invalid token at {i}: {sql[i]}"
                logger.error(error_msg)
                raise TokenizationError(error_msg)

        logger.info(f"Tokenized successfully: {tokens}")
        return tokens
