from .sensor import Sensor


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
