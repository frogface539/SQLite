class SQLiteCloneError(Exception):
    pass

class TokenizationError(SQLiteCloneError):
    def __init__(self , message):
        super().__init__(message)

class ParsingError(SQLiteCloneError):
    def __init__(self , message):
        super().__init__(message)

class ExecutionError(SQLiteCloneError):
    def __init__(self , message):
        super().__init__(message)
