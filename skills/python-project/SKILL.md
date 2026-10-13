---
name: python-project
description: Manage Python environments, dependencies, packaging, and CI in uv projects, or initialize a Python project when uv is requested. Not an instruction to migrate existing projects from other tools.
---

# Python Project

先检查已有 `pyproject.toml`、锁文件、Python 版本和 CI。保留项目现有工具；新项目默认可用 uv，用户指定其他工具时遵循用户选择。

## 选择项目形态

| 需要 | 起点 |
|---|---|
| 无依赖的一次性脚本 | 直接运行脚本，不必建包 |
| 有独立依赖的单文件脚本 | `uv init --script tool.py`，使用 PEP 723 元数据 |
| 应用 | `uv init myapp` |
| 可安装包或 CLI | `uv init --package myapp` |
| 库 | `uv init --lib mylib` |

目录只创建实际需要的部分。可安装包通常适合 `src/<package>/`；已有 flat layout 不必搬迁。测试按行为与边界组织，不要求目录逐层镜像源码。

## 常用操作

```bash
uv add requests                         # 运行依赖
uv add --dev pytest ruff                 # dev 依赖组
uv add --group lint ruff                 # 其他依赖组
uv remove requests
uv sync                                 # 同步项目环境
uv run pytest                           # 使用项目环境运行
uv run ruff check .
uv lock --upgrade-package requests      # 有目的地更新单个依赖
uv export --format requirements-txt --output-file requirements.txt
```

上面的包是命令示例，不是每个项目都要安装的依赖清单。`uv run` 默认会检查锁定和同步；仅使用现有环境时可用 `--no-sync`。

开发工具放在 `[dependency-groups]`；`uv sync --group lint` 安装相应组。`--extra` 对应 `[project.optional-dependencies]` 中供消费者选择的可选功能，二者不要混淆。

## 入口与 CI

可安装包的 CLI 入口使用 Python callable：

```toml
[project.scripts]
myapp = "myapp.cli:main"
```

安装项目后运行 `uv run myapp`。测试与 lint 直接用 `uv run pytest` 和 `uv run ruff check .`；uv 没有供任意 shell 命令别名使用的 `[tool.uv.scripts]`。

CI 通常用 `uv sync --locked`，再运行 `uv run --locked pytest` 等既定检查。`--locked` 在锁文件与声明不一致时失败；`--frozen` 跳过一致性检查，只在确实需要该行为时使用。

提交 `pyproject.toml` 和项目的 `uv.lock`，忽略 `.venv/`。通过 uv 修改依赖和锁文件。Python 版本按部署与依赖约束选择：`requires-python` 声明支持范围，`.python-version` 选择本地解释器；不硬编码教程中的版本为升级目标。

## 查证入口

命令或配置有疑问时先看已安装版本的 `uv <command> --help`，再查官方文档：

- [项目配置](https://docs.astral.sh/uv/concepts/projects/config/)
- [依赖与依赖组](https://docs.astral.sh/uv/concepts/projects/dependencies/)
- [锁定与同步](https://docs.astral.sh/uv/concepts/projects/sync/)
- [单文件脚本](https://docs.astral.sh/uv/guides/scripts/)
