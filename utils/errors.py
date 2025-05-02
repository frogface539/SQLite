class SQLiteCloneError(Exception):
    pass

class TokenizationError(SQLiteCloneError):
    pass

class ParsingError(SQLiteCloneError):
    pass

class ExecutionError(SQLiteCloneError):
    pass
