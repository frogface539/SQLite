from utils.errors import ParsingError
from utils.logger import get_logger

logger = get_logger(__name__)

def parse_select(self):
        self.consume()  # Consuming SELECT keyword
        col = self.parse_columns()
        current = self.current_token()

        if current and current.token_type == "KEYWORD" and current.value == "FROM":
            self.consume()  # Consuming FROM keyword
            tables = self.parse_tables() 
            logger.info(f"SELECT parsed: columns = {col}, tables = {tables}")  
            return {"type": "SELECT", "columns": col, "tables": tables}  
        
        else:
            logger.error("Expected 'FROM' in SELECT statement.")
            raise ParsingError("Expected 'FROM' in SELECT statement.")
        
