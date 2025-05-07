import re
from abc import ABC, abstractmethod

class Validator(ABC):
    @abstractmethod
    def validate(self, value) -> tuple[bool, str]:
        pass

class Range(Validator):
    def __init__(self, min=None, max=None):
        self.min = min
        self.max = max

    def validate(self, value):
        if self.min is not None and value < self.min:
            return False, f"Value must be ≥ {self.min}"
        if self.max is not None and value > self.max:
            return False, f"Value must be ≤ {self.max}"
        return True, ""

class Regex(Validator):
    def __init__(self, pattern: str, message="Invalid format"):
        self.pattern = re.compile(pattern)
        self.message = message

    def validate(self, value):
        return (bool(self.pattern.fullmatch(str(value))), self.message)

class OneOf(Validator):
    def __init__(self, choices):
        self.choices = choices

    def validate(self, value):
        return (value in self.choices, f"Must be one of: {', '.join(map(str, self.choices))}")
