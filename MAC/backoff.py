import random

class MILDBackoffCounter:
    """
        This class implements the MILD (Multiplicative Increase, Linear Decrease) counter
        that defined in MACAW paper.
    """

    def __init__(self, minimum, maximum):
        self._minimum = minimum
        self._maximum = maximum

        self._current = minimum

    def increase(self):
        self._current = min(self._current * 1.5, self._maximum)

    def decrease(self):
        self._current = max(self._current - 1, self._minimum)

    def get(self) -> float:
        return self._current

    def set(self, other: float):
        # Effin' python and its syntax lol
        if self._minimum <= other <= self._maximum:
            self._current = other

    def random(self) -> int:
        return random.randint(self._minimum, round(self._current))
