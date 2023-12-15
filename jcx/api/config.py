from pydantic import BaseModel


class Endpoint(BaseModel):
    host: str
    port: int

    def __str__(self) -> str:
        return '%s:%d' % (self.host, self.port)


class ApiCfg(BaseModel):
    name: str
    root: str
    endpoint: Endpoint

    def url(self, scheme: str) -> str:
        """获取URL"""
        return '%s://%s/%s' % (scheme, self.endpoint, self.root)


def test_cfg() -> None:
    _cfg = ApiCfg(name='配置', root='/howell/ias', endpoint=Endpoint(host='localhost', port=5000))
    assert _cfg.name == '配置'
