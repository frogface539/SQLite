from utils.errors import ParsingError
from utils.logger import get_logger

logger = get_logger(__name__)

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0  # Setting initial position

    def parse(self):
        if not self.tokens:
            logger.error("No tokens found")
            raise ParsingError("No tokens found")
        
        return self.sql_statement()
    
    def current_token(self):
        if self.index < len(self.tokens):
            return self.tokens[self.index]
        return None
    
    def consume(self):
        token = self.current_token()
        logger.debug(f"Processed token: {token}")
        self.index += 1
        return token
    
    def sql_statement(self):
        current = self.current_token()

        if current and current.token_type == "KEYWORD" and current.value == "SELECT":
            logger.info("Parsing SELECT statement")
            return self.select_statement()
        
        elif current and current.token_type == "KEYWORD" and current.value == "INSERT":
            logger.info("Parsing INSERT statement.")
            return self.insert_statement()
        
        else:
            logger.error(f"Invalid SQL statement found: {current}")
            raise ParsingError(f"Invalid SQL statement found: {current}")
        
    def select_statement(self):
        self.consume()  # Consuming SELECT keyword
        col = self.columns()
        current = self.current_token()

        if current and current.token_type == "KEYWORD" and current.value == "FROM":
            self.consume()  # Consuming FROM keyword
            table = self.table_name()
            logger.info(f"SELECT parsed: columns = {col}, table = {table}")
            return {"type": "SELECT", "columns": col, "table": table}
        
        else:
            logger.error("Expected 'FROM' in SELECT statement.")
            raise ParsingError("Expected 'FROM' in SELECT statement.")
        
    def columns(self):
        columns = []
        current = self.current_token()

        if current and current.token_type == "ASTERISK":
            logger.debug("Found '*' , selecting all columns....")
            self.consume()  # Consuming '*'
            return ['*']
        
        while current and current.token_type == "IDENTIFIER":
            logger.debug(f"Found Column: {current.value}")
            columns.append(current.value)
            self.consume()
            current = self.current_token()
            if current and current.token_type == "COMMA":
                self.consume()  # Consume the comma
                current = self.current_token()
            else:
                break

        if not columns:
            logger.error("Expected at least one column in SELECT statement.")
            raise ParsingError("Expected at least one column in SELECT statement.")
        
        return columns
    
    def table_name(self):
        current = self.current_token()
        if current and current.token_type == "IDENTIFIER":
            logger.debug(f"Found table name: {current.value}")
            self.consume()
            return current.value
        else:
            logger.error("Expected a table name..")
            raise ParsingError("Expected a table name..")
        
    def insert_statement(self):
        self.consume()  # INSERT
        self.consume()  # INTO

        table = self.table_name()

        current = self.current_token()
        if current and current.token_type == "KEYWORD" and current.value == "VALUES":
            self.consume()  # VALUES keyword
            values = self.values()
            logger.info(f"INSERT parsed: table={table}, values={values}")
            return {"type": "INSERT", "table": table, "values": values}
        else:
            logger.error("Expected 'VALUES' in INSERT statement.")
            raise ParsingError("Expected 'VALUES' in INSERT statement.")

    def values(self):
        values = []
        current = self.current_token()

        while current and current.token_type in ("QUOTE", "NUMBER"):  # Handle string or number values
            logger.debug(f"Found value: {current.value}")
            values.append(current.value)
            self.consume()
            current = self.current_token()
            if current and current.token_type == "COMMA":
                self.consume()  # Consume the comma
                current = self.current_token()
            else:
                break

        if not values:
            logger.error("Expected at least one value in INSERT statement.")
            raise ParsingError("Expected at least one value in INSERT statement.")

        return values
