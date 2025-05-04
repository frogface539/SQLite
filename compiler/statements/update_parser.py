from utils.errors import ParsingError
from utils.logger import get_logger

logger = get_logger(__name__)

def parse_update(self):
    logger.info("Parsing UPDATE statement...")

    self.consume()  # Consume 'UPDATE' keyword
    table_token = self.current_token()  # Get the next token, which should be the table name
    
    if table_token.token_type != "IDENTIFIER":
        logger.error(f"Expected table name after UPDATE, but found: {table_token.value}")
        raise ParsingError(f"Expected table name after UPDATE, but found: {table_token.value}")
    
    table_name = table_token.value
    logger.debug(f"Table name identified: {table_name}")

    self.advance()  # Move past the table name token

    # Check for the SET keyword
    self.expect("KEYWORD", "SET")
    self.advance()  # Move past the SET keyword

    updates = self.parse_set_clause()  # Update 'set' to 'updates'
    logger.debug(f"SET clause: {updates}")

    # Check for an optional WHERE clause
    where_clause = None
    if self.current_token().token_type == "KEYWORD" and self.current_token().value.upper() == "WHERE":
        self.consume()  # Consume WHERE
        where_clause = self.parse_where_clause()
        logger.debug(f"WHERE clause: {where_clause}")

    return {
        "type": "UPDATE",
        "table_name": table_name,
        "updates": updates,  # Change 'set' to 'updates'
        "where": where_clause
    }
