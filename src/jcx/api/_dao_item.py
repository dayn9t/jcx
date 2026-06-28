from pathlib import Path
from typing import Any

from cattr import structure, unstructure

# NON-LOCKED-LIB: flask-restx, pending selection decision (architecture: Web layer should be Rust/axum)
# flask-restx has no type stubs; per-module ignore_missing_imports in pyproject
from flask_restx import Api, Namespace, Resource
from pydantic import BaseModel

from jcx.db.jdb.variant import JdbVariant


class ItemDao[R: BaseModel]:
    """条目数据访问对象（单模型存储，无 id 主键约束）"""

    def __init__(self, record_type: type[R], folder: Path, name: str) -> None:
        self._var = JdbVariant(record_type, folder, name)

    def value_type(self) -> type[R]:
        """获取条目类型"""
        return self._var.value_type()

    def variant(self) -> JdbVariant[R]:
        """获取数据变量"""
        return self._var

    def get(self) -> R | None:
        """获取指定记录"""
        return self._var.get().unwrap_or(None)

    def update(self, r: R) -> R | None:
        """更新记录"""
        r0: R | None = self.get()
        r1 = self.before_update(r, r0)
        if not r1:
            return r1
        self._var.set(r1)
        self.after_update(r1)
        return r1

    def before_update(self, r: R, _r0: R | None) -> R | None:
        """更新记录之前的检查, 可修改r值"""
        return r

    def after_update(self, r: R) -> None:
        """更新记录之后的检查, 不可修改r值"""


def make_item[R: BaseModel](api: Api, data: dict[str, object], item_type: type[R]) -> tuple[bool, R]:
    """从数据构建条目"""
    try:
        item = structure(data, item_type)
    except TypeError as e:
        return False, api.abort(400, str(e))
    return True, item


def add_item_resource[R: BaseModel](
    ns: Namespace, url: str, dao: ItemDao[R], model: dict[str, object]
) -> None:
    """添加独立资源"""
    # TODO: model 通过 record_type 动态生成

    @ns.route(url)
    class Item(Resource):  # type: ignore[misc]  # flask-restx Resource 无 stub，推断为 Any
        """展示所有条目列表, 允许创建新条目"""

        @ns.doc("get_item")  # type: ignore[untyped-decorator]  # flask-restx 装饰器无 stub
        @ns.marshal_with(model)  # type: ignore[untyped-decorator]
        def get(self) -> dict[str, Any]:
            """获取条目"""
            r = dao.get()
            # unstructure 返回动态 dict（cattr 序列化结果）；flask-restx marshal 处理
            return unstructure(r)  # type: ignore[no-any-return]

        @ns.expect(model)  # type: ignore[untyped-decorator]
        @ns.marshal_with(model)  # type: ignore[untyped-decorator]
        def put(self) -> tuple[dict[str, Any], int]:
            """修改条目"""
            ok, r = make_item(self.api, self.api.payload, dao.value_type())
            if not ok:
                return r  # type: ignore[return-value]  # make_item 失败分支 r 来自 api.abort(Any)
            r1 = unstructure(dao.update(r))
            if not r1:
                return self.api.abort(400, "更新条目失败")  # type: ignore[no-any-return]
            return r1, 201
