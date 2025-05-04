from utils.errors import ParsingError
from utils.logger import get_logger
from compiler.statements.create_parser import parse_create
from compiler.statements.select_parser import parse_select
from compiler.statements.insert_parser import parse_insert
from compiler.statements.update_parser import parse_update
from compiler.statements.drop_parser import parse_drop
from compiler.statements.delete_parser import parse_delete

logger = get_logger(__name__)

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0  # Setting initial position

    def current_token(self):
        """Returns the current token."""
        if self.index < len(self.tokens):
            return self.tokens[self.index]
        return None

    def advance(self):
        """Advance to the next token in the token stream."""
        self.index += 1

    def consume(self):
        """Consumes the current token and advances the pointer."""
        token = self.current_token()
        logger.debug(f"Processed token: {token}")
        self.index += 1
        return token

    def expect(self, token_type, value=None):
        """Ensure the next token matches the expected type (and value)."""
        token = self.current_token()
        if not token:
            raise ParsingError(f"Expected {token_type} but reached end of input.")

        if token.token_type != token_type or (value is not None and token.value != value):
            raise ParsingError(f"Expected {token_type} '{value}' but got '{token.token_type}' '{token.value}'")

        self.consume()
        return token

    def parse(self):
        """Main entry point for parsing SQL queries."""
        if not self.tokens:
            logger.error("No tokens found")
            raise ParsingError("No tokens found")
        
        return self.sql_statement()

    def sql_statement(self):
        """Identifies the SQL statement type and dispatches to appropriate parser."""
        current = self.current_token()

        if current.token_type == "KEYWORD":
            value = current.value.upper()

            if value == "SELECT":
                return parse_select(self)
            elif value == "INSERT":
                return parse_insert(self)
            elif value == "CREATE":
                return parse_create(self)
            elif value == "DROP":
                return parse_drop(self)
            elif value == "DELETE":
                return parse_delete(self)
            elif value == "UPDATE":
                return parse_update(self)

        logger.error(f"Invalid SQL statement: {current}")
        raise ParsingError(f"Invalid SQL statement: {current.value}")

    def table_name(self):
        logger.debug("Parsing table name....")
        
        token = self.current_token()
        logger.debug(f"Current token in table_name: {token}")

        if not token:
            logger.error("Unexpected end of input while parsing table name")
            raise ParsingError("Unexpected end of input while parsing table name")
        
        if token.token_type != "IDENTIFIER":
            logger.error(f"Expected table name, but got {token.value}")
            raise ParsingError(f"Expected table name, but got {token.value}")
        
        table_name = token.value
        logger.debug(f"Table Name Found: {table_name}")
        
        self.consume()
        return table_name



    def values(self):
        """Returns the list of values for statements like INSERT."""
        values = []
        current = self.current_token()

        while current and current.token_type in ("NUMBER", "STRING"):
            logger.debug(f"Found value: {current.value}")
            values.append(current.value)
            self.consume()
            current = self.current_token()
            if current and current.token_type == "COMMA":
                self.consume()
                current = self.current_token()
            else:
                break

        if not values:
            logger.error("Expected at least one value in INSERT statement.")
            raise ParsingError("Expected at least one value in INSERT statement.")

        return values


    def condition(self):
        logger.debug("Parsing WHERE condition....")
        column = self.current_token().value
        logger.debug(f"Column Found: {column}")
        self.consume()

        if self.current_token().token_type != "EQUALS":
            logger.error("Expected '=' after column name in WHERE clause.")
            raise ParsingError("Expected '=' after column name in WHERE clause.")
        
        self.consume()  # Consume '=' token

        value = self.current_token().value
        logger.debug(f"Value Found: {value}")
        self.consume()

        return {"column": column, "value": value}

    def parse_set_clause(self):
        updates = {}
        while self.current_token().token_type == "IDENTIFIER":
            column = self.current_token().value
            self.advance()

            self.expect("EQUALS")
            self.advance()

            value = self.current_token().value
            updates[column] = value

            self.advance()  # Move past the value token
            if self.current_token().value != ",":
                break
            self.advance()  # Move past the comma for the next update, if any
        
        return updates

    def parse_columns(self):
        columns = []
        while self.current_token() and self.current_token().token_type == 'IDENTIFIER':
            columns.append(self.current_token().value)
            self.advance()

            # If there are more columns, expect a comma and a valid column name
            if self.current_token() and self.current_token().value == ",":
                self.advance()  # consume comma
                if not (self.current_token() and self.current_token().token_type == 'IDENTIFIER'):
                    raise ParsingError("Expected column name after ','")
        return columns
    
    def parse_tables(self):
        """Parses the table(s) in the SQL statement."""
        tables = []
        current = self.current_token()

        while current and current.token_type == "IDENTIFIER":
            tables.append(current.value)
            self.consume()  # consume the table name
            current = self.current_token()
            
        
            if current and current.token_type == "COMMA":
                self.consume()  # consume the comma
                current = self.current_token()

        if not tables:
            raise ParsingError("Expected table name in the query.")
        
        return tables
