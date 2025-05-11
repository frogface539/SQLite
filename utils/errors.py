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

class CodegenError(SQLiteCloneError):
    """Errors during code generation"""
    def __init__(self, message):
        super().__init__(f"Code Generation Error: {message}")
        self.message = message
