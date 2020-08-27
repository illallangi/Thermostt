from os.path import basename
from sys import argv, stderr

from click import Choice as CHOICE, FLOAT, INT, STRING, group, option

from loguru import logger

from notifiers.logging import NotificationHandler

from .controller import Controller
from .health import Health
from .load import Load
from .sensor import Sensor
from .vmax import VMax
from .vmin import VMin


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
        default=__package__)
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

    logger.success(f'{basename(argv[0])} Started')
    logger.info('  --log-level "{}"', log_level)
    if slack_webhook:
        logger.info('  --slack-webhook "{}"', slack_webhook)
        logger.info('  --slack-username "{}"', slack_username)
        logger.info('  --slack-format "{}"', slack_format)


@cli.command(name='run', context_settings={"auto_envvar_prefix": "THERMOSTT"})
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
@option('--qe', type=STRING, required=False)
@option('--qe-topic', type=STRING, required=False)
@option('--qe-value', type=STRING, required=False)
@option('--load-topic', type=STRING, required=False)
@option('--load-jmespath', type=STRING, required=False)
@option('--load-health', type=STRING, required=False)
@option('--load-health-topic', type=STRING, required=False)
@option('--load-health-jmespath', type=STRING, required=False)
@option('--load-health-healthy', type=STRING, required=False)
@option('--sensor', type=STRING, required=True)
@option('--sensor-delta', type=FLOAT, required=False, default=0.0)
@option('--sensor-topic', type=STRING, required=False)
@option('--sensor-jmespath', type=STRING, required=False)
@option('--sensor-health', type=STRING, required=False)
@option('--sensor-health-topic', type=STRING, required=False)
@option('--sensor-health-jmespath', type=STRING, required=False)
@option('--sensor-health-healthy', type=STRING, required=False)
@option('--vmax', type=STRING, required=False)
@option('--vmax-delta', type=FLOAT, required=False, default=0.0)
@option('--vmax-topic', type=STRING, required=False)
@option('--vmax-jmespath', type=STRING, required=False)
@option('--vmin', type=STRING, required=False)
@option('--vmin-delta', type=FLOAT, required=False, default=0.0)
@option('--vmin-topic', type=STRING, required=False)
@option('--vmin-jmespath', type=STRING, required=False)
@option('--state-topic', type=STRING, required=False)
@option('--lwt-topic', type=STRING, required=False)
def run(
        server,
        port,
        sensor,
        sensor_delta,
        sensor_topic,
        sensor_jmespath,
        sensor_health,
        sensor_health_topic,
        sensor_health_jmespath,
        sensor_health_healthy,
        vmax,
        vmax_delta,
        vmax_topic,
        vmax_jmespath,
        vmin,
        vmin_delta,
        vmin_topic,
        vmin_jmespath,
        load,
        q0,
        q0_topic,
        q0_value,
        q1,
        q1_topic,
        q1_value,
        qe,
        qe_topic,
        qe_value,
        load_topic,
        load_jmespath,
        load_health,
        load_health_topic,
        load_health_jmespath,
        load_health_healthy,
        name,
        state_topic,
        lwt_topic):

    logger.info('  run')
    if server:
        logger.info('    --server "{}"', server)
    if port:
        logger.info('    --port "{}"', port)
    if sensor:
        logger.info('    --sensor "{}"', sensor)
    if sensor_delta:
        logger.info('    --sensor-delta "{}"', sensor_delta)
    if sensor_topic:
        logger.info('    --sensor-topic "{}"', sensor_topic)
    if sensor_jmespath:
        logger.info('    --sensor-jmespath "{}"', sensor_jmespath)
    if sensor_health:
        logger.info('    --sensor-health "{}"', sensor_health)
    if sensor_health_topic:
        logger.info('    --sensor-health-topic "{}"', sensor_health_topic)
    if sensor_health_jmespath:
        logger.info('    --sensor-health-jmespath "{}"', sensor_health_jmespath)
    if sensor_health_healthy:
        logger.info('    --sensor-health-healthy "{}"', sensor_health_healthy)
    if vmax:
        logger.info('    --vmax "{}"', vmax)
    if vmax_delta:
        logger.info('    --vmax-delta "{}"', vmax_delta)
    if vmax_topic:
        logger.info('    --vmax-topic "{}"', vmax_topic)
    if vmax_jmespath:
        logger.info('    --vmax-jmespath "{}"', vmax_jmespath)
    if vmin:
        logger.info('    --vmin "{}"', vmin)
    if vmin_delta:
        logger.info('    --vmin-delta "{}"', vmin_delta)
    if vmin_topic:
        logger.info('    --vmin-topic "{}"', vmin_topic)
    if vmin_jmespath:
        logger.info('    --vmin-jmespath "{}"', vmin_jmespath)
    if load:
        logger.info('    --load "{}"', load)
    if q0:
        logger.info('    --q0 "{}"', q0)
    if q0_topic:
        logger.info('    --q0-topic "{}"', q0_topic)
    if q0_value:
        logger.info('    --q0-value "{}"', q0_value)
    if q1:
        logger.info('    --q1 "{}"', q1)
    if q1_topic:
        logger.info('    --q1-topic "{}"', q1_topic)
    if q1_value:
        logger.info('    --q1-value "{}"', q1_value)
    if qe:
        logger.info('    --qe "{}"', qe)
    if qe_topic:
        logger.info('    --qe-topic "{}"', qe_topic)
    if qe_value:
        logger.info('    --qe-value "{}"', qe_value)
    if load_topic:
        logger.info('    --load-topic "{}"', load_topic)
    if load_jmespath:
        logger.info('    --load-jmespath "{}"', load_jmespath)
    if load_health:
        logger.info('    --load-health "{}"', load_health)
    if load_health_topic:
        logger.info('    --load-health-topic "{}"', load_health_topic)
    if load_health_jmespath:
        logger.info('    --load-health-jmespath "{}"', load_health_jmespath)
    if load_health_healthy:
        logger.info('    --load-health-healthy "{}"', load_health_healthy)
    if name:
        logger.info('    --name "{}"', name)
    if state_topic:
        logger.info('    --state-topic "{}"', state_topic)
    if lwt_topic:
        logger.info('    --lwt-topic "{}"', lwt_topic)

    Controller(
        server,
        port,
        Load(
            load,
            q0=None if q0 is None else q0.split(','),
            q0_topic=q0_topic,
            q0_value=q0_value,
            q1=None if q1 is None else q1.split(','),
            q1_topic=q1_topic,
            q1_value=q1_value,
            qe=None if qe is None else qe.split(','),
            qe_topic=qe_topic,
            qe_value=qe_value,
            topic=load_topic,
            jmespath=load_jmespath),
        Sensor(
            sensor,
            topic=sensor_topic,
            jmespath=sensor_jmespath,
            delta=sensor_delta),
        VMax(
            vmax or name,
            topic=vmax_topic,
            jmespath=vmax_jmespath,
            delta=vmax_delta),
        VMin(
            vmin or name,
            topic=vmin_topic,
            jmespath=vmin_jmespath,
            delta=vmin_delta),
        [
            Health(
                sensor_health or sensor,
                topic=sensor_health_topic,
                jmespath=sensor_health_jmespath,
                healthy=None if sensor_health_healthy is None else sensor_health_healthy.split(',')),
            Health(
                load_health or load,
                topic=load_health_topic,
                jmespath=load_health_jmespath,
                healthy=None if load_health_healthy is None else load_health_healthy.split(',')),
        ],
        name=name,
        lwt_topic=lwt_topic,
        state_topic=state_topic).connect().loop_forever()


if __name__ == "__main__":
    cli()
