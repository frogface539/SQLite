from utils.errors import ParsingError
from utils.logger import get_logger

logger = get_logger(__name__)

def parse_update(self):
    logger.info("Parsing UPDATE statement...")

    self.consume()  # UPDATE
    table_name = self.table_name()
    logger.debug(f"UPDATE table: {table_name}")

    if self.current_token().value != "SET":
        logger.error("Expected 'SET' after table name in UPDATE.")
        raise ParsingError("Expected 'SET' after table name.")

    self.consume()  # SET
    set_clause = self.parse_set_clause()
    logger.debug(f"SET clause: {set_clause}")

    where_clause = None
    current = self.current_token()
    if current and current.token_type == "KEYWORD" and current.value == "WHERE":
        self.consume()  # WHERE
        where_clause = self.condition()
        logger.debug(f"WHERE condition: {where_clause}")

    logger.info(f"UPDATE parsed: table = {table_name}, SET = {set_clause}, WHERE = {where_clause}")
    return {"type": "UPDATE", "table": table_name, "set": set_clause, "where": where_clause}


