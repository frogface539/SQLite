class Token:
    def __init__(self, token_type, value, position):
        self.token_type = token_type
        self.value = value
        self.position = position  

    def __repr__(self):
        return f"Token(type = {self.token_type}, value = {self.value}, position = {self.position})"
