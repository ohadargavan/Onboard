from abc import ABC, abstractmethod


class Condition(ABC):
    """
    Interface for conditions
    """

    @abstractmethod
    def check(self, payload: dict) -> str:
        pass


class MatchCondition(Condition):
    """
    Used for "MATCH" conditions in JSON
    checks equality between payload and expected value
    for example: decision == 'passed_interview'
    """

    def __init__(self, field: str, expected: str):
        self.field = field
        self.expected = expected

    def check(self, payload: dict) -> str:
        value = payload.get(self.field)
        if value == self.expected:
            return "passed"
        return "failed"


class ThresholdCondition(Condition):
    """
    Used for "THRESHOLD" conditions in JSON
    Checks if value is greater than threshold
    """

    def __init__(self, field: str, value: int):
        self.field = field
        self.value = value

    def check(self, payload: dict) -> str:

        score = payload.get(self.field, 0)
        if score > self.value:
            return "passed"
        return "failed"


class RangeCondition(Condition):
    """
    Used for "RANGE" conditions in JSON
    returns the outcome for the relevant range
    """

    def __init__(self, field: str, rules: list):
        self.field = field
        self.rules = rules

    def check(self, payload: dict) -> str:
        score = payload.get(self.field, 0)

        #Go over rules (min, max, outcome) defined in JSON
        for rule in self.rules:
            if rule['min'] <= score <= rule['max']:
                return rule['outcome']

        #If the value does not fit to any defined range
        return "failed"