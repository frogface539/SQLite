from utils.errors import ParsingError
from utils.logger import get_logger

logger = get_logger(__name__)

def parse_insert(parser):
    logger.debug("Parsing INSERT statement...")
    parser.consume()  # Consume INSERT

    parser.expect("KEYWORD", "INTO")
    table_name = parser.table_name()

    parser.expect("LPAREN")
    columns = parser.parse_columns()
    parser.expect("RPAREN")

    parser.expect("KEYWORD", "VALUES")
    
    all_values = []
    while True:
        parser.expect("LPAREN")
        values = []
        
        # Parse values until RPAREN
        while True:
            current = parser.current_token()
            if not current:
                raise ParsingError("Unexpected end of input in VALUES clause")
            
            if current.token_type == "RPAREN":
                parser.consume()
                break
            
            # Handle different value types
            if current.token_type in ("NUMBER", "STRING"):
                values.append(current.value)
                parser.consume()
            elif current.token_type == "KEYWORD" and current.value.upper() == "NULL":
                values.append(None)
                parser.consume()
            elif current.token_type == "KEYWORD" and current.value.upper() in ("TRUE", "FALSE"):
                values.append(current.value.upper() == "TRUE")
                parser.consume()
            else:
                raise ParsingError(f"Invalid value type {current.token_type}")
            
            # Handle comma or end of group
            if parser.current_token().token_type == "COMMA":
                parser.consume()
            elif parser.current_token().token_type != "RPAREN":
                raise ParsingError("Expected comma or closing parenthesis")
        
        all_values.append(values)
        
        # Check for more value groups
        if parser.current_token().token_type == "COMMA":
            parser.consume()
            continue
        break
    
    parser.expect("SEMICOLON")

    if len(all_values) > 1:
        logger.warning("Multi-row INSERT detected - only first row will be processed")
    
    return {
        "type": "INSERT",
        "table_name": table_name,
        "columns": columns,
        "values": all_values[0]  # Currently only handling first row
    }