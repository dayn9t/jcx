from jcx.net.mqtt.publisher import *


def test_publish() -> None:
    cfg = MqttCfg('tcp://localhost:1883', 'howell/ias')

    publisher = Publisher(cfg)

    publisher.publish('sources/11', 'hi 11!')
