from utils.errors import ParsingError
from utils.logger import get_logger

logger = get_logger(__name__)
def parse_drop(self):
    logger.info("Parsing DROP statement....")
    self.consume() #consuming drop

    if self.current_token().value != "TABLE":
        logger.error("Expected 'TABLE' after DROP")
        raise ParsingError("Expected 'TABLE' after DROP")
    
    self.consume() # consuming table
    table_name = self.table_name()
    logger.debug(f"DROP TABLE: {table_name}")

    logger.info(f"Dropped Table: {table_name}")
    return {"type" : "DROP" , "table_name" : table_name}