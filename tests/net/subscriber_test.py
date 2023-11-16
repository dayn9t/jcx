from jcx.net.mqtt.subscriber import *


class Outputer:
    def on_mqtt_message(self, mqtt_msg: MQTTMessage):
        assert self
        print('Outputer:', msg.payload)


def demo_sub():
    """FIXME: 不能用单元测试, 会卡死在消息分发"""
    outputer = Outputer()

    cfg = MqttCfg('tcp://localhost:1883', 'howell')
    subcriber = Subscriber(cfg)

    # subcriber.loop(lambda msg: print(msg))
    subcriber.dispatch_msg('1/#', outputer)
