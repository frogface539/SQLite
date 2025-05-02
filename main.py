from compiler.tokenizer import Tokenizer
from utils.errors import SQLiteCloneError
from utils.logger import get_logger

logger = get_logger(__name__)

def main():
    tokenizer = Tokenizer()
    while True:
        try:
            sql = input("sqlite> ").strip()
            if sql.lower() == "exit":
                break
            tokens = tokenizer.tokenize(sql)
            print("Tokens:", tokens)
        except SQLiteCloneError as e:
            logger.error(f"Error: {e}")
        except Exception as e:
            logger.exception("Unexpected error")

if __name__ == "__main__":
    main()
