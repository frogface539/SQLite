from utils.errors import ParsingError
from utils.logger import get_logger

logger = get_logger(__name__)

def parse_drop(self):
    logger.info("Parsing DROP statement....")
    self.consume()

    current_token = self.current_token()
    if current_token.token_type != "IDENTIFIER":
        logger.error("Expected an entity after DROP (e.g., TABLE, VIEW, etc.)")
        raise ParsingError("Expected an entity after DROP (e.g., TABLE, VIEW, etc.)")

    entity_name = current_token.value
    logger.debug(f"Dropped Entity: {entity_name}")

    self.consume()

    if self.current_token().value != ";":
        logger.error("Expected ';' at the end of DROP statement")
        raise ParsingError("Expected ';' at the end of DROP statement")

    logger.info(f"DROP parsed: entity = {entity_name}")
    return {"type": "DROP", "table_name": entity_name}
