from enum import Enum, auto, unique


@unique
class LoadState(Enum):
    Q0 = auto()
    Q1 = auto()

    def __str__(self):
        return self.name
