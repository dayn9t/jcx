import os
from typing import Protocol
from urllib.parse import urlparse

# NON-LOCKED-LIB: paho-mqtt + loguru, pending selection decision
import paho.mqtt.client as mqtt
from loguru import logger

from jcx.net.mqtt.cfg import MqttCfg


class MqttListener(Protocol):
    """MQTT 消息监听者协议（user_object 须实现 on_mqtt_message）"""

    def on_mqtt_message(self, msg: mqtt.MQTTMessage) -> None:
        """处理收到的 MQTT 消息"""
        ...


class Subscriber:
    """MQTT消息订阅者"""

    def __init__(self, cfg: MqttCfg) -> None:
        """创建MQTT消息订阅者"""
        uri = urlparse(cfg.server_url)
        strs = uri.netloc.split(":", 1)
        self.url = cfg.server_url
        self.hostname: str = strs[0]
        self.port: int = int(strs[1])
        self.transport: str = uri.scheme
        self.root_topic = cfg.root_topic
        self.client = mqtt.Client(protocol=mqtt.MQTTv5)
        self.client.on_message = on_message

    def dispatch_msg(
        self, topic: str, user_object: MqttListener, timeout: float = 8.0
    ) -> None:
        """分发消息"""
        self.client.user_data_set(user_object)

        topic = os.path.join(self.root_topic, topic)
        logger.info(f"Subscribe mqtt topic: {self.url}/{topic} ...")

        self.client.connect(self.hostname, self.port, 60)
        self.client.subscribe(topic, 0)

        self.client.loop_forever(timeout=timeout)


def on_message(
    _client: mqtt.Client, user_object: MqttListener, msg: mqtt.MQTTMessage
) -> None:
    user_object.on_mqtt_message(msg)
