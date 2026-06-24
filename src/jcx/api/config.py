from pydantic import BaseModel


class Endpoint(BaseModel):
    host: str
    port: int

    def __str__(self) -> str:
        return "%s:%d" % (self.host, self.port)


class ApiCfg(BaseModel):
    name: str
    root: str
    endpoint: Endpoint

    def url(self, scheme: str) -> str:
        """获取URL"""
        return f"{scheme}://{self.endpoint}/{self.root}"
