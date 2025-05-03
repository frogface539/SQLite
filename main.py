from compiler.tokenizer import Tokenizer
from compiler.parser import Parser
from utils.errors import TokenizationError, ParsingError

# Initialize Tokenizer
tokenizer = Tokenizer()

# Prompt user for a SQL query
# query = input("Enter your SQL query: ")
query = "select column1 from table1, table2 where table1.id = table2.id;"

print(f"Parsing Query: {query}")

try:
    # Tokenizing the query
    tokens = tokenizer.tokenize(query)
    print(f"Tokens: {tokens}")

    # Initialize Parser with the tokens
    parser = Parser(tokens)

    # Parse the SQL statement
    result = parser.parse()
    print(f"Parsed Result: {result}")

except TokenizationError as e:
    print(f"Tokenization Error: {e}")
except ParsingError as e:
    print(f"Parsing Error: {e}")
except Exception as e:
    print(f"Unexpected Error: {e}")
