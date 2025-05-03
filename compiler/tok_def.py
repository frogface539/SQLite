class Token:
    def __init__(self, type_,value,position=None):
        self.type = type_
        self.value = value
        self.position = position

    def __repr__(self):
        return f'Token(type = {self.type}, value = {self.value}), position = {self.position}'