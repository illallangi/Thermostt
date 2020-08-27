from enum import Enum, auto, unique


@unique
class HealthState(Enum):
    Healthy = auto()
    Unhealthy = auto()

    def __str__(self):
        return self.name
