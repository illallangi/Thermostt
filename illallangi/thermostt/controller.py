from datetime import datetime
from functools import cached_property
from json import dumps, loads

from loguru import logger

from paho.mqtt.client import Client

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

        self.name = name or __package__
        self.lwt_topic = lwt_topic or f'tele/{self.name}/LWT'.replace('.', '_')
        self.state_topic = state_topic or f'tele/{self.name}/STATE'.replace('.', '_')

    def __str__(self):
        o = {
            'time': datetime.utcnow().isoformat(),
            'sensor': self.sensor.value,
            'vmax': self.vmax.value,
            'vmin': self.vmin.value,
            'load': self.load.value.name if self.load.value else None,
            'target': self.target.name if 'target' in self.__dict__ and self.target is not self.load.value else None,
        }

        return dumps({
            k: o[k]
            for k in o
            if o[k]
        })

    @cached_property
    def client(self):
        c = Client()
        c.on_connect = self.on_connect
        c.on_message = self.on_message
        c.will_set(self.lwt_topic, 'Offline', qos=0, retain=False)
        return c

    def connect(self):
        self.client.connect(self.server, self.port, 60)
        self.client.publish(self.lwt_topic, 'Online', qos=0, retain=False)
        return self.client

    def loop_forever(self):
        self.client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        logger.info('Connected with result code {}', rc)
        self.client.subscribe(self.load.topic)
        self.client.subscribe(self.sensor.topic)
        self.client.subscribe(self.vmax.topic)
        self.client.subscribe(self.vmin.topic)

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

        if self.load.value and \
           self.sensor.value and \
           self.vmax.value and \
           self.vmin.value:

            if self.sensor.value >= self.vmax.value and \
               self.load.value is LoadState.Q0:
                self.target = LoadState.Q1
                logger.debug('Switching to Q1 with {}: {}', self.load.q1_topic, self.load.q1_value)
                self.client.publish(self.load.q1_topic, self.load.q1_value, qos=0, retain=False)

            if self.sensor.value <= self.vmin.value and \
               self.load.value is LoadState.Q1:
                self.target = LoadState.Q0
                logger.debug('Switching to Q0 with {}: {}', self.load.q0_topic, self.load.q0_value)
                self.client.publish(self.load.q0_topic, self.load.q0_value, qos=0, retain=False)

        self.client.publish(
            self.state_topic,
            str(self),
            qos=0,
            retain=False)