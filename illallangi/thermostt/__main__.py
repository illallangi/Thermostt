from sys import stderr

from click import Choice as CHOICE, FLOAT, INT, STRING, group, option

from loguru import logger

from notifiers.logging import NotificationHandler

from .controller import Controller
from .load import Load
from .sensor import Sensor, VMax, VMin


@group()
@option('--log-level',
        type=CHOICE(['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'SUCCESS', 'TRACE'],
                    case_sensitive=False),
        default='INFO')
@option('--slack-webhook',
        type=STRING,
        envvar='SLACK_WEBHOOK',
        default=None)
@option('--slack-username',
        type=STRING,
        envvar='SLACK_USERNAME',
        default=__name__)
@option('--slack-format',
        type=STRING,
        envvar='SLACK_FORMAT',
        default='{message}')
def cli(log_level, slack_webhook, slack_username, slack_format):
    logger.remove()
    logger.add(stderr, level=log_level)

    if slack_webhook:
        params = {
            "username": slack_username,
            "webhook_url": slack_webhook
        }
        slack = NotificationHandler("slack", defaults=params)
        logger.add(slack, format=slack_format, level="SUCCESS")


@cli.command(name='run')
@option('--server', type=STRING, required=True)
@option('--port', type=INT, required=False, default=1883)
@option('--name', type=STRING, required=False)
@option('--load', type=STRING, required=True)
@option('--q0', type=STRING, required=False)
@option('--q0-topic', type=STRING, required=False)
@option('--q0-value', type=STRING, required=False)
@option('--q1', type=STRING, required=False)
@option('--q1-topic', type=STRING, required=False)
@option('--q1-value', type=STRING, required=False)
@option('--load-topic', type=STRING, required=False)
@option('--load-jmespath', type=STRING, required=False)
@option('--sensor', type=STRING, required=True)
@option('--sensor-topic', type=STRING, required=False)
@option('--sensor-jmespath', type=STRING, required=False)
@option('--vmax', type=STRING, required=False)
@option('--vmax-value', type=FLOAT, required=False)
@option('--vmax-topic', type=STRING, required=False)
@option('--vmax-jmespath', type=STRING, required=False)
@option('--vmin', type=STRING, required=False)
@option('--vmin-value', type=FLOAT, required=False)
@option('--vmin-topic', type=STRING, required=False)
@option('--vmin-jmespath', type=STRING, required=False)
@option('--state-topic', type=STRING, required=False)
@option('--lwt-topic', type=STRING, required=False)
def run(
        server,
        port,
        sensor,
        sensor_topic,
        sensor_jmespath,
        vmax,
        vmax_value,
        vmax_topic,
        vmax_jmespath,
        vmin,
        vmin_value,
        vmin_topic,
        vmin_jmespath,
        load,
        q0,
        q0_topic,
        q0_value,
        q1,
        q1_topic,
        q1_value,
        load_topic,
        load_jmespath,
        name,
        state_topic,
        lwt_topic):
    Controller(
        server,
        port,
        Load(
            load,
            q0=q0,
            q0_topic=q0_topic,
            q0_value=q0_value,
            q1=q1,
            q1_topic=q1_topic,
            q1_value=q1_value,
            topic=load_topic,
            jmespath=load_jmespath),
        Sensor(
            sensor,
            topic=sensor_topic,
            jmespath=sensor_jmespath),
        VMax(
            vmax or name,
            topic=vmax_topic,
            jmespath=vmax_jmespath,
            value=vmax_value),
        VMin(
            vmin or name,
            topic=vmin_topic,
            jmespath=vmin_jmespath,
            value=vmin_value),
        name=name,
        lwt_topic=lwt_topic,
        state_topic=state_topic).connect().loop_forever()


if __name__ == "__main__":
    cli()
