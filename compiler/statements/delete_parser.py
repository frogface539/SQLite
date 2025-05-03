from utils.logger import get_logger
from utils.errors import ParsingError

logger = get_logger(__name__)

def parse_delete(self):
    logger.info("Parsing DELETE statement....")
    self.consume() # delete

    if self.current_token().value != "FROM":
        logger.error("Expected 'FROM' after DELETE...")
        raise ParsingError("Expected 'FROM' after DELETE...")
    
    self.consume() # FROM
    table_name = self.table_name()
    logger.debug(f"DELETE FROM: {table_name}")

    # where parsing
    where_token = None
    current = self.current_token()
    if current and current.token_type == "KEYWORD" and current.value == "WHERE":

        self.consume() # WHERE
        where_token = self.condition()
        logger.debug(f"WHERE condition: {where_token}")

    logger.info(f"DELETE parsed: table = {table_name}, WHERE condition = {where_token}")
    return {"type":"DELETE" , "table" : table_name , "where" : where_token}
