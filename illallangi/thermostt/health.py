from jmespath import compile
from jmespath.parser import ParsedResult

from loguru import logger

from .healthstate import HealthState


class Health(object):
    def __init__(
            self,
            name,
            *args,
            topic=None,
            jmespath=None,
            healthy=None,
            **kwargs):
        super().__init__(
            *args,
            **kwargs)
        self.topic = topic or f'tele/{name}/LWT'
        self.jmespath = jmespath or 'payload'
        self.jmespath = compile(self.jmespath) if not isinstance(self.jmespath, ParsedResult) else self.jmespath
        self.healthy = healthy or ['Online']
        logger.debug('Subscribed to {} with jmespath filter {}', self.topic, self.jmespath)

    @property
    def value(self):
        return self._value if '_value' in self.__dict__ else None

    @value.setter
    def value(self, value):
        self._value = value

    def __str__(self):
        return str(self.value)

    def on_message(self, payload):
        try:
            filtered_json = self.jmespath.search(payload)
        except Exception as e:
            logger.error('Error filtering: {}', str(e))
            return

        try:
            result = str(filtered_json)
        except Exception as e:
            logger.error('Error casting to str: {}', str(e))
            return

        if result in self.healthy:
            self.value = HealthState.Healthy
            return
        self.value = HealthState.Unhealthy
