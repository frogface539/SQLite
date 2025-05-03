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
        raise ParsingError(f"Invalid SQL statement: {current}")
         
    #                        ================= HELPER FUNCTIONS ==================
    

    def table_name(self):
       
        current = self.current_token()
        if current and current.token_type == "IDENTIFIER":
            logger.debug(f"Found table name: {current.value}")
            self.consume()
            return current.value
        else:
            logger.error("Expected a table name..")
            raise ParsingError("Expected a table name..")
        

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

    def parse_set_clause(self):
        set_clause = []
        current = self.current_token()

        while current and current.token_type == "IDENTIFIER":
            column = current.value
            self.consume()

            if self.current_token().value != "=":
                logger.error("Expected '=' after column name in SET clause.")
                raise ParsingError("Expected '=' after column name in SET clause.")
            self.consume()  # '='

            value = self.current_token().value
            self.consume()

            set_clause.append((column, value))

            if self.current_token().token_type == "COMMA":
                self.consume()
            else:
                break

        return set_clause
    
    def condition(self):
        column = self.consume()  # Assuming consume returns a token
        if column.token_type != "IDENTIFIER":
            raise ParsingError(f"Expected column name, but found {column.value}")

        operator = self.consume()  # '='
        if operator.token_type != "EQUALS":
            raise ParsingError(f"Expected '=' operator, but found {operator.value}")

        value = self.consume()  # a number or string
        if value.token_type not in ["NUMBER", "STRING"]:
            raise ParsingError(f"Expected a value for condition, but found {value.value}")

        return {"column": column.value, "operator": operator.value, "value": value.value}
    
    def parse_columns(self):
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
    
    def parse_tables(self): 
        tables = []
        current = self.current_token()

        while current and current.token_type == "IDENTIFIER":
            logger.debug(f"Found Table: {current.value}")
            tables.append(current.value)
            self.consume()
            current = self.current_token()
            if current and current.token_type == "COMMA":
                self.consume()  # Consume the comma
                current = self.current_token()
            else:
                break

        if not tables:
            logger.error("Expected at least one table in SELECT statement.")
            raise ParsingError("Expected at least one table in SELECT statement.")
            
        return tables 

    
    