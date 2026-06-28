from typing import Literal
from urllib.parse import urlparse

# NON-LOCKED-LIB: paho-mqtt, pending selection decision
from paho.mqtt import publish

from jcx.net.mqtt.cfg import MqttCfg
from jcx.text.txt_json import to_json

# paho.mqtt publish.single 接受的 transport 取值
Transport = Literal["tcp", "websockets"]


def _parse_transport(scheme: str) -> Transport:
    """URL scheme → paho transport；非 tcp/websockets 一律视为 tcp"""
    return "websockets" if scheme in ("ws", "wss", "websockets") else "tcp"


class Publisher:
    """MQTT 消息发布者"""

    def __init__(self, cfg: MqttCfg) -> None:
        uri = urlparse(cfg.server_url)
        strs = uri.netloc.split(":", 1)
        self.hostname: str = strs[0]
        self.port: int = int(strs[1])
        self.transport: Transport = _parse_transport(uri.scheme)
        self.root_topic = cfg.root_topic

    def publish(self, topic: str, msg: object) -> None:
        """发布消息（任意可序列化对象，经 JSON 序列化后发送）"""
        s = to_json(msg)
        publish.single(
            self.root_topic + "/" + topic,
            s,
            hostname=self.hostname,
            port=self.port,
            transport=self.transport,
        )
