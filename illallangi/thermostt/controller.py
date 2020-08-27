from datetime import datetime
from functools import cached_property
from json import dumps, loads

from loguru import logger

from paho.mqtt.client import Client

from .healthstate import HealthState
from .loadstate import LoadState


class Controller(object):
    def __init__(
            self,
            server,
            port,
            load,
            sensor,
            vmax,
            vmin,
            health,
            *args,
            name=None,
            lwt_topic=None,
            state_topic=None,
            **kwargs):
        super().__init__(
            *args,
            **kwargs)

        self.server = server
        self.port = port

        self.load = load
        self.sensor = sensor
        self.vmax = vmax
        self.vmin = vmin
        self.health = health

        self.name = name or __package__
        self.lwt_topic = lwt_topic or f'tele/{self.name}/LWT'.replace('.', '_')
        self.state_topic = state_topic or f'tele/{self.name}/STATE'.replace('.', '_')

    def __str__(self):
        o = {
            'time': datetime.utcnow().isoformat(),
            'sensor': self.sensor.value,
            'vmax': self.vmax.value,
            'vmin': self.vmin.value,
            'load': self.load.value,
            'target': self.target.name if 'target' in self.__dict__ and self.target != self.load else None,
        }

        return dumps({
            k: o[k]
            for k in o
            if o[k]
        })

    @property
    def healthy(self):
        return self.load.value and \
            self.sensor.value and \
            self.vmax.value and \
            self.vmin.value and \
            HealthState.Unhealthy not in (h.value for h in self.health)

    @cached_property
    def client(self):
        c = Client()
        c.on_connect = self.on_connect
        c.on_message = self.on_message
        c.will_set(self.lwt_topic, 'Offline', qos=0, retain=False)
        return c

    def connect(self):
        self.client.connect(self.server, self.port, 60)
        self.client.publish(self.lwt_topic, 'Online' if self.healthy else 'Error', qos=0, retain=False)
        return self.client

    def loop_forever(self):
        self.client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        logger.info('Connected with result code {}', rc)
        self.client.subscribe(self.load.topic)
        self.client.subscribe(self.sensor.topic)
        self.client.subscribe(self.vmax.topic)
        self.client.subscribe(self.vmin.topic)
        for health in self.health:
            self.client.subscribe(health.topic)

    def on_message(self, client, userdata, msg):
        try:
            decoded_payload = msg.payload.decode('UTF-8')
        except Exception as e:
            logger.error('Error decoding payload: {}', str(e))
            return

        try:
            payload = {'payload': loads(decoded_payload)}
        except ValueError:
            payload = {'payload': decoded_payload}
        except Exception as e:
            logger.error('Error decoding json: {}', str(e))
            return

        logger.trace(payload)

        if msg.topic == self.load.topic:
            self.load.on_message(payload)

        if msg.topic == self.sensor.topic:
            self.sensor.on_message(payload)

        if msg.topic == self.vmax.topic:
            self.vmax.on_message(payload)

        if msg.topic == self.vmin.topic:
            self.vmin.on_message(payload)

        for health in self.health:
            if msg.topic == health.topic:
                health.on_message(payload)

        if self.healthy:
            if self.sensor.value >= self.vmax.value and \
               (self.load == LoadState.Q0 or self.target != LoadState.Q1):
                self.target = LoadState.Q1
                logger.success('Switching to Q1 with {}: {}', self.load.q1_topic, self.load.q1_value)
                self.client.publish(self.load.q1_topic, self.load.q1_value, qos=0, retain=False)

            if self.sensor.value <= self.vmin.value and \
               (self.load == LoadState.Q1 or self.target != LoadState.Q0):
                self.target = LoadState.Q0
                logger.success('Switching to Q0 with {}: {}', self.load.q0_topic, self.load.q0_value)
                self.client.publish(self.load.q0_topic, self.load.q0_value, qos=0, retain=False)
        elif self.load != LoadState.Qe:
            self.target = LoadState.Qe
            logger.success('Switching to Qe with {}: {}', self.load.qe_topic, self.load.qe_value)
            self.client.publish(self.load.qe_topic, self.load.qe_value, qos=0, retain=False)

        self.client.publish(self.lwt_topic, 'Online' if self.healthy else 'Error', qos=0, retain=False)
        self.client.publish(
            self.state_topic,
            str(self),
            qos=0,
            retain=False)
