from jcx.net.mqtt.publisher import *


def test_publish() -> None:
    cfg = MqttCfg(server_url="tcp://localhost:1883", root_topic="howell/ias")

    publisher = Publisher(cfg)

    publisher.publish("sources/11", "hi 11!")
