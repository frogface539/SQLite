from utils.errors import ParsingError
from utils.logger import get_logger

logger = get_logger(__name__)

def parse_create(self):
    logger.info("Parsing Create Table.... \n")
    self.consume()

    if self.current_token().value != "TABLE":
        logger.error("Expected 'TABLE' after CREATE.....")
        raise ParsingError("Expected 'TABLE' after CREATE.....")
    
    self.consume()

    columns = []
    logger.debug("Parsing Columns.....")

    while True:
        col_token = self.current_token()
        if col_token.token_type != "IDENTIFIER":
            logger.error("Expected column name...")
            raise ParsingError("Expected column name...")
        
        col_name = col_token.value
        logger.debug(f"Column Found: {col_name}")
        self.consume()

        type_token = self.current_token()
        if type_token.token_type != "KEYWORD":
            logger.error("Expected Column Type...")
            raise ParsingError("Expected Column Type...")
        
        col_type = type_token.value
        logger.debug(f"Column Type: {col_type}")
        self.consume()

        columns.append((col_name , col_type))

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
    return {"type":"CREATE" , "columns" : columns}