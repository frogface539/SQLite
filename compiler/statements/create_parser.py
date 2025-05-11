from utils.errors import ParsingError
from utils.logger import get_logger

logger = get_logger(__name__)

def parse_create(parser):
    parser.expect("KEYWORD", "CREATE")
    parser.expect("KEYWORD", "TABLE")
    table_name = parser.table_name()
    parser.expect("LPAREN")
    
    columns = []
    while True:
        col_name = parser.expect("IDENTIFIER").value
        col_type = parser.expect("KEYWORD").value  
        
        constraints = []
        while True:
            token = parser.current_token()
            if not token or token.token_type in ("COMMA", "RPAREN"):
                break
                
            if token.token_type == "IDENTIFIER":
                constraint = token.value.upper()
                if constraint in ["PRIMARY", "NOT"]:
                    next_token = parser.tokens[parser.index + 1] if parser.index + 1 < len(parser.tokens) else None
                    if constraint == "PRIMARY" and next_token and next_token.value.upper() == "KEY":
                        parser.consume()
                        parser.consume()
                        constraints.append("PRIMARY KEY")
                    elif constraint == "NOT" and next_token and next_token.value.upper() == "NULL":
                        parser.consume()  
                        parser.consume()  
                        constraints.append("NOT NULL")
                else:
                    parser.consume()
                    constraints.append(constraint)
            else:
                parser.consume()
        
        columns.append((col_name, col_type, constraints))
        
        token = parser.current_token()
        if not token or token.token_type == "RPAREN":
            break
        parser.expect("COMMA")
    
    parser.expect("RPAREN")
    
    parser.schema_registry[table_name] = [col['name'] for col in columns]
    logger.info(f"Updated schema registry with table {table_name}")
    
    return {
        "type": "CREATE",
        "table_name": table_name,
        "columns": columns
    }

    