from utils.errors import ParsingError
from utils.logger import get_logger

logger = get_logger(__name__)

def parse_select(parser):
    logger.debug("Parsing SELECT statement...")
    parser.expect("KEYWORD", "SELECT")
    
    columns = []
    if parser.current_token().token_type == "ASTERISK":
        columns.append("*")
        parser.consume()
    else:
        columns = parser.parse_columns()

    parser.expect("KEYWORD", "FROM")
    tables = parser.parse_tables()
    
    if len(tables) != 1:
        raise ParsingError("Only single table SELECT supported at the moment.")

    result = {
        "type": "SELECT",
        "columns": columns,
        "table_name": tables[0],
    }

    if parser.current_token() and parser.current_token().value.upper() == "WHERE":
        parser.consume()
        result["where"] = parser.condition()

    return result