from utils.errors import ParsingError
from utils.logger import get_logger

logger = get_logger(__name__)

def parse_create(self):
    logger.info("Parsing Create Table.... \n")
    self.consume()

    if self.current_token().value != "TABLE":
        logger.error("Expected 'TABLE' after CREATE.....\n")
        raise ParsingError("Expected 'TABLE' after CREATE.....")
    
    self.consume()

    table_name = self.current_token().value  # Capture the table name
    logger.debug(f"Table Name Found: {table_name}")
    self.consume()

    # Expect opening parenthesis '('
    if self.current_token().value != "(":
        logger.error("Expected '(' after table name...\n")
        raise ParsingError("Expected '(' after table name...")
    
    self.consume()

    columns = []
    logger.debug("Parsing Columns.....\n")

    while True:
        col_token = self.current_token()

        if col_token.token_type != "IDENTIFIER":
            logger.error(f"Expected column name, but got {col_token.token_type} - {col_token.value}")
            raise ParsingError("Expected column name...")
        
        col_name = col_token.value
        logger.debug(f"Column Found: {col_name}")
        self.consume()

        # Check for the column type
        type_token = self.current_token()
        if type_token.token_type != "KEYWORD":
            logger.error(f"Expected column type (e.g., INT, TEXT), but got {type_token.token_type} - {type_token.value}")
            raise ParsingError("Expected Column Type...")
        
        col_type = type_token.value
        logger.debug(f"Column Type: {col_type}")
        self.consume()

        columns.append((col_name, col_type))

        token = self.current_token()
        if token.token_type == "COMMA":
            logger.debug("Found ',' moving to next column....")
            self.consume()

        elif token.token_type == "RPAREN":
            logger.debug("Found ')' moving to next column....")
            self.consume()
            break
        else:
            logger.error("Expected ',' or ')' in column list")
            raise ParsingError("Expected ',' or ')' in column list")
    
    logger.info(f"CREATE TABLE parsed successfully with columns: {columns}")
    return {"type": "CREATE", "table_name": table_name, "columns": columns}
