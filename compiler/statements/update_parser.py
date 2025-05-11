from utils.errors import ParsingError
from utils.logger import get_logger

logger = get_logger(__name__)

def parse_update(self):
    """Parse an UPDATE statement with robust error handling and logging"""
    logger.info("Starting UPDATE statement parsing")
    
    try:
        # Parse UPDATE keyword
        self.expect("KEYWORD", "UPDATE")
        logger.debug("Consumed UPDATE keyword")
        
        # Parse table name with detailed validation
        if not self.current_token():
            raise ParsingError("Unexpected end of input after UPDATE")
            
        current_token = self.current_token()
        valid_table_token = (
            current_token.token_type == "IDENTIFIER" or
            (current_token.token_type == "KEYWORD" and current_token.value.upper() == "TABLE")
        )
        
        if not valid_table_token:
            error_msg = (f"Expected table name after UPDATE, got "
                       f"'{current_token.value}' ({current_token.token_type}) at position {current_token.position}")
            logger.error(error_msg)
            raise ParsingError(error_msg)
        
        table_name = current_token.value
        self.consume()
        logger.debug(f"Identified table: {table_name}")

        # Parse SET clause with careful token handling
        self.expect("KEYWORD", "SET")
        logger.debug("Found SET keyword")
        
        # Don't consume next token yet - let parse_set_clause handle it
        try:
            updates = self.parse_set_clause()
            if not updates:
                raise ParsingError("SET clause must contain at least one column assignment")
            logger.debug(f"Parsed {len(updates)} column assignments")
        except ParsingError as e:
            logger.error(f"SET clause parsing failed: {str(e)}")
            raise ParsingError(f"Invalid SET clause: {str(e)}") from e

        # Parse optional WHERE clause
        where_clause = None
        if self.current_token() and (self.current_token().token_type == "KEYWORD" and 
                                   self.current_token().value.upper() == "WHERE"):
            self.consume()
            logger.debug("Parsing WHERE clause")
            try:
                where_clause = self.condition()
                logger.debug(f"Parsed condition: {where_clause}")
            except ParsingError as e:
                logger.error(f"WHERE clause error: {str(e)}")
                raise ParsingError(f"Invalid WHERE clause: {str(e)}") from e

        # Final validation
        if self.current_token() and self.current_token().token_type != "SEMICOLON":
            logger.warning(f"Unexpected token at end of UPDATE: {self.current_token().value}")

        logger.info(f"Successfully parsed UPDATE statement for table '{table_name}'")
        return {
            "type": "UPDATE",
            "table_name": table_name,
            "updates": updates,
            "where": where_clause
        }

    except ParsingError:
        raise  # Re-raise already logged parsing errors
    except Exception as e:
        logger.critical(f"Unexpected error during UPDATE parsing: {str(e)}", exc_info=True)
        raise ParsingError(f"Failed to parse UPDATE statement: {str(e)}") from e