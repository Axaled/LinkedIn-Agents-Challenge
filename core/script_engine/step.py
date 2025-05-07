class Step:
    def __init__(self, prompt: str, var: str, type_: type, validators=None):
        self.prompt = prompt
        self.var = var
        self.type_ = type_
        self.validators = validators or []
