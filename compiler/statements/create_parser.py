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
        col_type_token = parser.current_token()
        
        if col_type_token.token_type in ("KEYWORD", "IDENTIFIER"):
            col_type = col_type_token.value.upper()
            parser.consume()  # Consume the type token
            
            col_size = None
            if col_type == "VARCHAR":
                if parser.current_token() and parser.current_token().token_type == "LPAREN":
                    parser.consume()  # Consume '('
                    size_token = parser.expect("NUMBER")
                    col_size = int(size_token.value)
                    parser.expect("RPAREN")  # Expect ')'
        else:
            raise ParsingError(f"Expected data type, got {col_type_token}")

        constraints = []
        while True:
            token = parser.current_token()
            if not token or token.token_type in ("COMMA", "RPAREN"):
                break
                
            if token.token_type == "IDENTIFIER":
                constraint = token.value.upper()
                if constraint in ["PRIMARY", "NOT"]:
                    next_token = parser.peek_token()
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
        
        columns.append({
            "name": col_name,
            "type": col_type,
            "size": col_size,
            "constraints": constraints
        })
        
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