from utils.errors import ParsingError
from utils.logger import get_logger

logger = get_logger(__name__)

def parse_insert(parser):
    logger.debug("Parsing INSERT statement...")
    parser.consume()  

    parser.expect("KEYWORD", "INTO")  
    table_name = parser.table_name() 

    parser.expect("LPAREN") 
    columns = parser.parse_columns()  

    parser.expect("RPAREN")  

    parser.expect("KEYWORD", "VALUES") 
    parser.expect("LPAREN")  

    # Parse the values
    values = []
    current = parser.current_token()

    while current and current.token_type != "RPAREN":
        if current.token_type == "NUMBER" or current.token_type == "STRING":
            values.append(current.value)
            parser.consume() 

        if current.token_type == "COMMA":
            parser.consume()

        current = parser.current_token()

    
    if current and current.token_type == "RPAREN":
        parser.consume()  

    parser.expect("SEMICOLON")  

   
    result = {
        "type": "INSERT",
        "table_name": table_name,
        "columns": columns,
        "values": values
    }

    return result
