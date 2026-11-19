# pyproject 工具配置参考

仅在初始化新项目或用户明确要求调整工具配置时读取。向 `uv init` 生成的文件追加缺失配置；已有相同表时合并字段，不重复声明，也不覆盖无关设置。工具通过 `uv add --dev` 安装。

## 索引与源

默认不写索引配置，uv 使用 PyPI。只有用户或项目规范需要镜像时才设置默认索引，例如：

```toml
[[tool.uv.index]]
# 清华 PyPI 镜像
name = "tuna"
url = "https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple/"
default = true
```

项目依赖 CUDA 版 torch 时，再增加专用源，并用 `[tool.uv.sources]` 按平台限定：

```toml
[[tool.uv.index]]
# 仅服务 tool.uv.sources 中显式引用它的包
name = "pytorch-cu132"
url = "https://download.pytorch.org/whl/cu132"
explicit = true

[tool.uv.sources]
# Linux 使用 CUDA wheel；其他平台仍从默认索引解析
torch = [{ index = "pytorch-cu132", marker = "sys_platform == 'linux'" }]
```

镜像地址和 CUDA tag 按当前项目兼容性核实，不把示例当作固定版本。`explicit = true` 防止未点名的包从该源解析；缺少它或对应的 `torch` source 都会改变依赖来源。修改索引后重新 `uv lock` 和 `uv sync`。

## Ruff、Pyright 与 Pytest

以下以最低支持 Python 3.13，且实际存在 `src/`、`tests/`、`tools/` 的项目为例。根据 `requires-python` 调整版本，只保留真实目录，不为匹配模板创建空目录。

```toml
[tool.ruff]
line-length = 120
target-version = "py313"
src = ["src", "tests", "tools"]
extend-exclude = [".uv-cache", "tests/fixtures"]

[tool.ruff.lint]
select = [
    "E",   # pycodestyle：风格错误
    "W",   # pycodestyle：风格警告
    "F",   # Pyflakes：未使用导入、未定义变量
    "I",   # isort：导入排序
    "UP",  # pyupgrade：现代 Python 写法
    "B",   # flake8-bugbear：常见缺陷
    "C4",  # flake8-comprehensions：推导式与容器构造
    "SIM", # flake8-simplify：冗余逻辑
    "RUF", # Ruff 专属检查
]
# 项目文档与输出使用中文全角标点时，关闭同形字歧义检查。
ignore = ["RUF001", "RUF002", "RUF003"]

[tool.ruff.format]
# 同时格式化文档字符串中的示例代码。
docstring-code-format = true

[tool.pyright]
include = ["src", "tests", "tools"]
pythonVersion = "3.13"
typeCheckingMode = "standard"
```

已有测试目录时再配置 Pytest：

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra --strict-markers --strict-config"
```

`--strict-markers` 和 `--strict-config` 会把未声明的 marker 与配置错误变成失败；新增 marker 时在 `markers` 中声明。
