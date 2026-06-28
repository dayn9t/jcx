from typing import Any

from cattr import structure, unstructure

# NON-LOCKED-LIB: flask-restx, pending selection decision (architecture: Web layer should be Rust/axum)
# flask-restx has no type stubs; per-module ignore_missing_imports in pyproject
from flask_restx import Api, Namespace, Resource

from jcx.db.jdb.table import Table
from jcx.db.record import PRecord
from jcx.sys.fs import StrPath


class ItemListDao[R: PRecord]:
    """条目集合数据访问对象"""

    def __init__(self, record_type: type[R], folder: StrPath) -> None:
        self._tab = Table.open(record_type, folder)

    def record_type(self) -> type[R]:
        """获取记录类型"""
        return self._tab.record_type()

    def table(self) -> Table[R]:
        """获取数据表"""
        return self._tab

    def records(self) -> list[R]:
        """获取所有记录"""
        return self._tab.records()

    def get(self, rid: int) -> R | None:
        """获取指定记录"""
        return self._tab.get(rid).unwrap_or(None)

    def add(self, record: R) -> R | None:
        """添加新记录"""
        r = self.before_add(record)
        if r is None:
            return r

        added = self._tab.post(r)
        result = added.unwrap_or(None)
        if result is not None:
            self.after_add(result)
        return result

    def update(self, record: R) -> R | None:
        """更新记录"""
        r = self.before_update(record)
        if not r:
            return r
        result = self._tab.put(r)
        if result.is_null():
            return None
        updated = result.unwrap()
        self.after_update(updated)
        return updated

    def remove(self, record_id: int) -> None:
        """删除记录"""
        rid = self.before_remove(record_id)
        if not rid:
            return
        self._tab.remove(rid)
        self.after_remove(rid)

    def before_add(self, record: R) -> R | None:
        """添加新记录之前的检查"""
        return record

    def before_update(self, record: R) -> R | None:
        """更新记录之前的检查"""
        return record

    def before_remove(self, rid: int) -> int | None:
        """删除记录之前的检查"""
        return rid

    def after_add(self, record: R) -> None:
        """添加新记录之后的检查"""

    def after_update(self, record: R) -> None:
        """更新记录之后的检查"""

    def after_remove(self, rid: int) -> None:
        """删除记录之后的检查"""


def make_record[R: PRecord](
    api: Api, data: dict[str, object], record_type: type[R], id: int = 0
) -> tuple[bool, R]:
    """从数据构建记录"""
    if "id" not in data:
        data["id"] = id
    try:
        r = structure(data, record_type)
    except TypeError as e:
        return False, api.abort(400, str(e))
    return True, r


def add_list_resource(
    ns: Namespace, url: str, dao: ItemListDao[PRecord], model: dict[str, object]
) -> None:
    """添加集合资源"""
    # TODO: model 通过 record_type 动态生成

    @ns.route(url)
    class ItemList(Resource):  # type: ignore[misc]  # flask-restx Resource 无 stub，推断为 Any
        """展示所有条目列表, 允许创建新条目"""

        @ns.doc("list_items")  # type: ignore[untyped-decorator]  # flask-restx 装饰器无 stub
        @ns.marshal_list_with(model)  # type: ignore[untyped-decorator]
        def get(self) -> list[dict[str, Any]]:
            """列出所有条目"""
            rs = dao.records()
            # unstructure 返回动态 dict；flask-restx marshal 处理
            return list(map(unstructure, rs))

        @ns.doc("create_item")  # type: ignore[untyped-decorator]
        @ns.expect(model)  # type: ignore[untyped-decorator]
        @ns.marshal_with(model, code=201)  # type: ignore[untyped-decorator]
        def post(self) -> tuple[dict[str, Any], int]:
            """创建一个新条目"""
            ok, r = make_record(self.api, self.api.payload, dao.record_type())
            if not ok:
                return r  # type: ignore[return-value]  # make_record 失败分支 r 来自 api.abort(Any)
            r1 = unstructure(dao.add(r))
            if not r1:
                return self.api.abort(400, "创建条目失败")  # type: ignore[no-any-return]
            return r1, 201

    @ns.route(url + "/<int:id>")
    @ns.response(404, "指定条目未找到")
    @ns.param("id", "条目ID")
    class Item(Resource):  # type: ignore[misc]  # flask-restx Resource 无 stub，推断为 Any
        """展示一个单独的条目, 并允许修改和删除"""

        @ns.doc("get_item")  # type: ignore[untyped-decorator]
        @ns.marshal_with(model)  # type: ignore[untyped-decorator]
        def get(self, id: int) -> dict[str, Any]:
            """获取指定条目"""
            r = unstructure(dao.get(id))
            return r or self.api.abort(404, f"条目 {id} 不存在")  # type: ignore[no-any-return]

        @ns.doc("delete_item")  # type: ignore[untyped-decorator]
        @ns.response(204, "条目已经删除")  # type: ignore[untyped-decorator]
        def delete(self, id: int) -> tuple[str, int]:
            """删除指定ID的条目"""
            dao.remove(id)
            return "", 204

        @ns.expect(model)  # type: ignore[untyped-decorator]
        @ns.marshal_with(model)  # type: ignore[untyped-decorator]
        def put(self, id: int) -> tuple[dict[str, Any], int]:
            """修改指定ID的条目"""
            ok, r = make_record(self.api, self.api.payload, dao.record_type(), id)
            if not ok:
                return r  # type: ignore[return-value]  # make_record 失败分支 r 来自 api.abort(Any)
            if r.id != id:
                return self.api.abort(422, "数据中ID于URL中ID不符")  # type: ignore[no-any-return]
            r1 = unstructure(dao.update(r))
            if not r1:
                return self.api.abort(400, "更新条目失败")  # type: ignore[no-any-return]
            return r1, 201
