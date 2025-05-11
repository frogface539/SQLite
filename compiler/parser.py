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
        self.index = 0
        logger.debug(f"Initialized parser with {len(tokens)} tokens")

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
        """Parse WHERE clause with flexible operator handling"""
        logger.debug("Parsing WHERE condition")
        
        try:
            # Get column name
            if not self.current_token() or self.current_token().token_type != "IDENTIFIER":
                raise ParsingError("Expected column name after WHERE")
            column = self.current_token().value
            self.consume()
            logger.debug(f"Found WHERE column: {column}")

            # Handle operators (including single = for equality)
            valid_operators = {
                "EQUALS": "=",         # Standard SQL equality
                "NOTEQUALS": "!=",
                "LESSTHAN": "<",
                "GREATERTHAN": ">",
                "LESSEQUAL": "<=",
                "GREATEREQUAL": ">=",
                "IDENTIFIER": None     # Handle column comparisons
            }

            if not self.current_token():
                raise ParsingError("Expected operator after column name")

            # Special case: allow column-to-column comparisons
            if self.current_token().token_type == "IDENTIFIER":
                operator = None  # Mark as column comparison
                right_column = self.current_token().value
                self.consume()
                return {
                    "type": "column_compare",
                    "left_column": column,
                    "right_column": right_column
                }

            # Standard operator handling
            if self.current_token().token_type not in valid_operators:
                raise ParsingError(
                    f"Expected comparison operator (=, !=, <, >, <=, >=), got {self.current_token().token_type}"
                )

            operator = valid_operators[self.current_token().token_type]
            self.consume()
            logger.debug(f"Found operator: {operator}")

            # Get comparison value
            if not self.current_token():
                raise ParsingError("Expected value after operator")

            value_token = self.current_token()
            valid_types = ("NUMBER", "STRING", "IDENTIFIER", "KEYWORD")
            
            if value_token.token_type not in valid_types:
                raise ParsingError(f"Invalid value type {value_token.token_type}")

            value = value_token.value
            self.consume()

            return {
                "type": "value_compare",
                "column": column,
                "operator": operator,
                "value": value
            }

        except ParsingError as e:
            logger.error(f"WHERE clause parsing failed at token {self.index}: {str(e)}")
            raise ParsingError(f"Invalid WHERE clause: {str(e)}") from e

    def parse_set_clause(self):
        """Parse SET clause with robust string handling"""
        updates = {}
        logger.debug(f"Starting SET clause parsing at index {self.index}")

        while True:
            try:
                # Get column name
                if not self.current_token() or self.current_token().token_type != "IDENTIFIER":
                    raise ParsingError("Expected column name in SET clause")
                column = self.current_token().value
                self.consume()
                logger.debug(f"Processing column assignment: {column}")

                # Verify equals sign
                if not self.current_token() or self.current_token().token_type != "EQUALS":
                    raise ParsingError("Expected '=' after column name")
                self.consume()

                # Parse the value
                if not self.current_token():
                    raise ParsingError("Expected value after '='")

                value_token = self.current_token()
                logger.debug(f"Processing value token: {value_token}")

                # Handle different value types
                if value_token.token_type == "STRING":
                    # For already tokenized strings (quotes included in token)
                    value = value_token.value[1:-1]  # Remove quotes
                    self.consume()
                elif value_token.token_type == "QUOTE":
                    # For separate quote tokens (legacy handling)
                    self.consume()  # Consume opening quote
                    if not self.current_token() or self.current_token().token_type != "STRING":
                        raise ParsingError("Expected string content between quotes")
                    value = self.current_token().value
                    self.consume()
                    if not self.current_token() or self.current_token().token_type != "QUOTE":
                        raise ParsingError("Expected closing quote")
                    self.consume()
                elif value_token.token_type in ("NUMBER", "IDENTIFIER"):
                    value = value_token.value
                    self.consume()
                elif (value_token.token_type == "KEYWORD" and 
                    value_token.value.upper() in ("TRUE", "FALSE", "NULL")):
                    value = value_token.value
                    self.consume()
                else:
                    raise ParsingError(f"Invalid value type {value_token.token_type}")

                updates[column] = value
                logger.debug(f"Assigned {column} = {value}")

                # Check for more assignments
                if not self.current_token() or self.current_token().token_type != "COMMA":
                    break

                self.consume()  # consume comma
                logger.debug("Found comma, expecting next assignment")

            except ParsingError as e:
                logger.error(f"SET clause parsing failed at index {self.index}: {str(e)}")
                raise

        if not updates:
            raise ParsingError("SET clause must contain at least one assignment")

        logger.info(f"Successfully parsed SET clause with {len(updates)} assignments")
        return updates

    def parse_columns(self):
        columns = []
        while self.current_token() and self.current_token().token_type == 'IDENTIFIER':
            columns.append(self.current_token().value)
            self.advance()

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
                self.consume() 
                current = self.current_token()

        if not tables:
            raise ParsingError("Expected table name in the query.")
        
        return tables
