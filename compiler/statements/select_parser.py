from utils.errors import ParsingError
from utils.logger import get_logger

logger = get_logger(__name__)

def parse_select(parser):
    logger.debug("Parsing SELECT statement...")
    parser.consume()  # consume SELECT

    columns = parser.parse_columns()

    current = parser.current_token()
    if not current or current.value.upper() != "FROM":
        raise ParsingError("Expected 'FROM' keyword in SELECT statement.")
    parser.consume()  # consume FROM

    tables = parser.parse_tables()
    if len(tables) != 1:
        raise ParsingError("Only single table SELECT supported at the moment.")

    result = {
        "type": "SELECT",
        "columns": columns,
        "table_name": tables[0],
    }


    current = parser.current_token()
    if current and current.value.upper() == "WHERE":
        parser.consume()  # consume WHERE
        result["where"] = parser.condition()

    return result

        
