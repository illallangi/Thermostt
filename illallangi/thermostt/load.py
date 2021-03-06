from jmespath import compile
from jmespath.parser import ParsedResult

from loguru import logger

from .loadstate import LoadState


class Load(object):
    def __init__(
            self,
            name,
            *args,
            topic=None,
            q0=None,
            q0_topic=None,
            q0_value=None,
            q1=None,
            q1_topic=None,
            q1_value=None,
            qe=None,
            qe_topic=None,
            qe_value=None,
            jmespath=None,
            **kwargs):
        super().__init__(
            *args,
            **kwargs)
        self.topic = topic or f'tele/{name}/STATE'

        self.q0 = q0 or ['OFF']
        self.q0_topic = q0_topic or f'cmnd/{name}/POWER'
        self.q0_value = q0_value or self.q0[0]

        self.q1 = q1 or ['ON']
        self.q1_topic = q1_topic or f'cmnd/{name}/POWER'
        self.q1_value = q1_value or self.q1[0]

        self.qe = qe or ['OFF']
        self.qe_topic = qe_topic or f'cmnd/{name}/POWER'
        self.qe_value = qe_value or self.qe[0]

        self.jmespath = jmespath or 'payload.POWER'
        self.jmespath = compile(self.jmespath) if not isinstance(self.jmespath, ParsedResult) else self.jmespath
        logger.debug('Subscribed to {} with jmespath filter {}', self.topic, self.jmespath)

    def __eq__(self, other):
        if isinstance(other, LoadState):
            if other is LoadState.Q0 and self.value in self.q0:
                return True
            if other is LoadState.Q1 and self.value in self.q1:
                return True
            if other is LoadState.Qe and self.value in self.qe:
                return True
            return False
        return super.__eq__(other)

    @property
    def value(self):
        return self._value if '_value' in self.__dict__ else None

    @value.setter
    def value(self, value):
        self._value = value

    def __str__(self):
        return self.value

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

        if result in self.q0 or result in self.q1 or result in self.qe:
            self.value = result
            return

        logger.error('Unhandled value {}', result)
        pass
