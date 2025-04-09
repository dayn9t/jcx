# TODO

## api

- 文档注释还不能动态定义，
    - @ns.doc中可能没法达成效果
    - 可能要实现装饰器
- 模型成员的注释也不能从类导入, FastAPI应该能解决
    - 获取成员方法：```from attr import fields as attr_fields```

## TODO

## 参考

- https://python-poetry.org/docs/
- [4个工具帮你轻松将python项目发布到生产环境](https://blog.csdn.net/weixin_38739735/article/details/133257783)
  - black — 用于格式化代码
  - pydoctyle — 确保代码文档符合Google的标准
  - pycln — 用于删除未使用的导入
  - trailing-whitespace — 用于删除额外的空格
  - unitest — 用于运行单元测试和检测破坏性更改
  - tox — 用于测试不同版本的Python