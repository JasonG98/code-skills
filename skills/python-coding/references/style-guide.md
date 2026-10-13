# 文档风格

仅在项目没有既有约定且需要写注释或 docstring 时采用。默认中文描述、英文半角标点，中英文之间留空格。

```python
from pathlib import Path


def read_settings(path: Path) -> str:
    """读取 UTF-8 配置文本, 保留原始换行.

    Args:
        path: 已由调用方确定的配置文件路径.

    Raises:
        OSError: 文件不存在或无法读取时抛出.
        UnicodeError: 内容不是有效 UTF-8 时抛出.
    """
    with path.open(encoding="utf-8", newline="") as stream:
        return stream.read()
```

签名已有的类型不重复到 docstring。使用 Args、Returns、Raises 中真正提供额外信息的部分；简单实现不需要填满模板。

注释记录不易从代码得出的原因，例如兼容约束或经过验证的性能取舍。避免给显然的赋值和循环写逐行说明；删除过期注释与注释掉的代码。
