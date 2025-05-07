from typing import Any
from core.script_engine.step import Step

class Script:
    def __init__(self, steps: list[Step]):
        self.steps = steps
        self.index = 0
        self.values = {}

    def current_step(self) -> Step | None:
        if self.index < len(self.steps):
            return self.steps[self.index]
        return None

    def _parse(self, raw: str, expected_type: type) -> Any | None:
        try:
            if expected_type == bool:
                return raw.lower() in ["yes", "true", "1", "oui"]
            return expected_type(raw)
        except Exception:
            return None

    def assign(self, user_input: str) -> str:
        step = self.current_step()
        if not step:
            return "🎉 All steps completed. Free chat may begin."

        parsed = self._parse(user_input, step.type_)
        if parsed is None:
            return f"❌ Expected a {step.type_.__name__}."

        for validator in step.validators:
            ok, msg = validator.validate(parsed)
            if not ok:
                return f"❌ {msg}"

        self.values[step.var] = parsed
        self.index += 1
        return f"Added: {step.var} = {parsed}"

    def next_prompt(self) -> str:
        step = self.current_step()
        if step:
            return step.prompt
        return "🎉 All steps completed. Free chat may begin."
