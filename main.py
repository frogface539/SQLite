from compiler.tokenizer import Tokenizer
from compiler.parser import Parser
from utils.errors import TokenizationError, ParsingError
from pprint import pprint 

# Initialize Tokenizer
tokenizer = Tokenizer()

# Prompt user for a SQL query
# query = input("Enter your SQL query: ")
query = "UPDATE products SET price = 799.99 WHERE id = 5;"


print(f"Parsing Query: {query}")

try:
    # Tokenizing the query
    tokens = tokenizer.tokenize(query)
    print("Tokens:")
    pprint(tokens)  

    # Initialize Parser with the tokens
    parser = Parser(tokens)

    # Parse the SQL statement
    result = parser.parse()
    print("Parsed Result:")
    pprint(result) 

except TokenizationError as e:
    print(f"Tokenization Error: {e}")
except ParsingError as e:
    print(f"Parsing Error: {e}")
except Exception as e:
    print(f"Unexpected Error: {e}")
