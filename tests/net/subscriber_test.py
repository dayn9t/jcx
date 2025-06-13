from paho.mqtt.client import MQTTMessage

from jcx.net.mqtt.subscriber import *


class Output:
    def on_mqtt_message(self, mqtt_msg: MQTTMessage) -> None:
        assert self
        print("Output:", mqtt_msg.payload)


def demo_sub() -> None:
    """FIXME: 不能用单元测试, 会卡死在消息分发"""
    output = Output()

    cfg = MqttCfg("tcp://localhost:1883", "howell")
    subscriber = Subscriber(cfg)

    # subscriber.loop(lambda msg: print(msg))
    subscriber.dispatch_msg("1/#", output)
