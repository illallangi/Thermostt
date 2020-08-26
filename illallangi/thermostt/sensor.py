from jmespath import compile
from jmespath.parser import ParsedResult

from loguru import logger


class Sensor(object):
    def __init__(
            self,
            name,
            *args,
            topic=None,
            jmespath=None,
            value=None,
            **kwargs):
        super().__init__(
            *args,
            **kwargs)
        self.topic = topic or f'tele/{name}/SENSOR'
        self.jmespath = jmespath or 'payload.DS18B20.Temperature'
        self.jmespath = compile(self.jmespath) if not isinstance(self.jmespath, ParsedResult) else self.jmespath
        self.value = value
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
            result = float(filtered_json)
        except Exception as e:
            logger.error('Error casting to float: {}', str(e))
            return

        self.value = result


class VMax(Sensor):
    def __init__(
            self,
            name,
            *args,
            topic=None,
            jmespath=None,
            **kwargs):
        super().__init__(
            name or __package__.replace('.', '_'),
            *args,
            topic=topic or f'cmnd/{name or __package__}/vmax'.replace('.', '_'),
            jmespath=jmespath or 'payload',
            **kwargs)


class VMin(Sensor):
    def __init__(
            self,
            name,
            *args,
            topic=None,
            jmespath=None,
            **kwargs):
        super().__init__(
            name or __package__.replace('.', '_'),
            *args,
            topic=topic or f'cmnd/{name or __package__}/vmin'.replace('.', '_'),
            jmespath=jmespath or 'payload',
            **kwargs)
