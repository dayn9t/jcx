import os
from urllib.parse import urlparse

import paho.mqtt.client as mqtt
from loguru import logger

from jcx.net.mqtt.cfg import MqttCfg


class Subscriber:
    """MQTT消息订阅者"""

    def __init__(self, cfg: MqttCfg) -> None:
        """创建MQTT消息订阅者"""
        uri = urlparse(cfg.server_url)
        strs = uri.netloc.split(":", 1)
        self.url = cfg.server_url
        self.params = {
            "transport": uri.scheme,
            "hostname": strs[0],
            "port": int(strs[1]),
        }
        self.root_topic = cfg.root_topic
        self.client = mqtt.Client(protocol=mqtt.MQTTv5)
        self.client.on_message = on_message

    def dispatch_msg(
        self, topic: str, user_object: object, timeout: float = 8.0
    ) -> None:
        """分发消息"""
        self.client.user_data_set(user_object)

        topic = os.path.join(self.root_topic, topic)
        logger.info(f"Subscribe mqtt topic: {self.url}/{topic} ...")

        self.client.connect(self.params["hostname"], self.params["port"], 60)
        self.client.subscribe(topic, 0)

        self.client.loop_forever(timeout=timeout)


def on_message(
    _client: mqtt.Client, user_object: object, msg: mqtt.MQTTMessage
) -> None:
    if user_object is not None:
        user_object.on_mqtt_message(msg)
