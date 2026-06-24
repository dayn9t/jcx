from urllib.parse import urlparse

from paho.mqtt import publish

from jcx.net.mqtt.cfg import MqttCfg
from jcx.text.txt_json import to_json


class Publisher:
    """MQTT 消息发布者"""

    def __init__(self, cfg: MqttCfg) -> None:
        uri = urlparse(cfg.server_url)
        strs = uri.netloc.split(":", 1)
        self.params = {
            "transport": uri.scheme,
            "hostname": strs[0],
            "port": int(strs[1]),
        }
        self.root_topic = cfg.root_topic

    def publish(self, topic: str, msg: object) -> None:
        """发布消息（任意可序列化对象，经 JSON 序列化后发送）"""
        s = to_json(msg)
        publish.single(self.root_topic + "/" + topic, s, **self.params)
