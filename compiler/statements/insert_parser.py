from utils.errors import ParsingError
from utils.logger import get_logger

logger = get_logger(__name__)

def parse_insert(self):
    logger.info("Parsing INSERT statement...")

    self.consume()  # INSERT
    self.consume()  # INTO

    table_name = self.table_name()
    logger.debug(f"INSERT INTO: {table_name}")

    if self.current_token().value != "VALUES":
        logger.error("Expected 'VALUES' after table name.")
        raise ParsingError("Expected 'VALUES' after table name.")
    
    self.consume()  # VALUES
    values = self.values()
    logger.debug(f"INSERT values: {values}")

    logger.info(f"INSERT parsed: table = {table_name}, values = {values}")
    return {"type": "INSERT", "table": table_name, "values": values}
