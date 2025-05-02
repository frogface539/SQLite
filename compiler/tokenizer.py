import re
#error handling
from utils.logger import get_logger
from utils.errors import TokenizationError

logger = get_logger(__name__)

class Tokenizer:
    def __init__(self):
        self.patterns = [ 

            ("KEYWORD" , r"\b(SELECT|FROM|INSERT|INTO|VALUES|CREATE|TABLE|WHERE|AND|OR|UPDATE|SET|DELETE|JOIN|ORDER|BY|GROUP)\b"),
            ("IDENTIFIER", r"[a-zA-Z_][a-zA-Z0-9_]*"),
            ("NUMBER" , r"\b\d+\b"),
            ("STRING" , r"'[^']*'"),
            ("SEMICOLON",r","),
            ("LPAREN",r"\("),
            ("RPAREN",r"\)"),
            ("OPERATOR",r"(=|!=|<=|>=|<|>)"),
            ("ASTERISK",r"\*")

        ]

    def tokenize(self,sql):
        tokens = []
        i=0
        sql = sql.strip() #removes trailing whitespaces

        while i < len(sql):

            # skip whitespaces
            if sql[i].isspace():
                i = i+1
                continue

            # skip single line comments "--"
            if sql[i : i+2] == "--":
                end = sql.find("\n",i)
                if end == -1:
                    break
                i = end + 1
                continue

            match_found = False
            for token_type , pattern in self.patterns:
                regex = re.compile(pattern,re.IGNORECASE)
                match = regex.match(sql,i)
                if match:
                    value = match.group(0)
                    token_value = value.upper() if token_type == "KEYWORD" else value

                    tokens.append((token_type , token_value))
                    logger.debug(f"Matched token:({token_type} , {token_value})")
                    i = match.end()
                    match_found = True
                    break

            if not match_found:
                raise TokenizationError(f"Unknown token at: '{sql[i:]}'")
            
            logger.info(f"Tokenized SQL: {tokens}")
            return tokens



