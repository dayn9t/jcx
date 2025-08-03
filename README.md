# JCX

一些基础功能库。

## TODO

- 通过单元测试, 因为改用 pydantic 导致大量问题
- python稀烂的泛型


## 打包

```bash
nuitka --job=8  --onefile --standalone --follow-imports --output-dir=dist src/jcx/bin/cx_task.py
```
