---
name: python-project
description: Scaffold new uv-based Python projects with tool configuration and an AGENTS.md command list, or manage environments, dependencies, packaging, and CI in existing uv projects. Do not migrate projects from other tools unless explicitly requested.
---

# Python Project

先区分新建项目与已有项目。已有项目的工具、布局、Python 版本和检查约定优先，只修改任务涉及的内容；不重新初始化、不套用新项目模板，也不自动迁移非 uv 项目。

## 新建 uv 项目

初始 `pyproject.toml` 必须由 `uv init` 生成，不手写或从模板复制。按项目形态选择命令：

| 需要 | 命令 |
|---|---|
| 无特殊布局要求的应用 | `uv init myapp` |
| 可安装包或 CLI | `uv init --package myapp` |
| 不需要 `build-system` 的应用 | `uv init --no-package myapp` |
| 库 | `uv init --lib mylib` |
| 有独立依赖的单文件脚本 | `uv init --script tool.py` |
| 无依赖的一次性脚本 | 直接运行脚本，不建项目 |

版本相关的默认布局先用 `uv init --help` 核对。生成后可以按真实需求修改元数据、依赖、入口、Python 支持范围和目录；禁止的是绕过 `uv init` 手写初始配置，不是后续维护。`uv.lock` 同样通过 uv 生成和更新。

新建应用、包或库时，按项目需要建立 Ruff、Pyright 和测试基线，通过 `uv add --dev` 安装实际使用的工具，例如：

```bash
uv add --dev pytest ruff pyright
```

读取 [pyproject 工具配置](references/pyproject-tooling.md) 后再修改配置。一次性脚本不强加完整工具链；已有项目只有用户要求标准化时才补齐。只创建实际需要的目录，已有 flat layout 不搬迁，测试目录不必逐层镜像源码。

## 记录项目命令

新项目完成配置后，在项目根目录 `AGENTS.md` 新增或更新 `## 命令`，一行一条并注明用途。已有文件的其他内容保持不变。通用命令可按实际配置选用：

```markdown
## 命令

uv sync                         # 安装依赖
uv run ruff check .             # 静态检查
uv run ruff format --check .    # 格式检查
uv run pyright                  # 类型检查，必须无报错
uv run pytest                   # 单元测试
```

未安装的工具不写，没有测试时不保留 pytest 行。项目自己的运行、训练或导出命令按真实入口和参数补充，不照抄其他项目；GPU、外部资源和长耗时条件要在注释里说明。

安全的常规检查在记录前实际运行。长耗时、需要特殊硬件或有副作用的命令至少核验入口与参数，不要求为写文档完整执行，也不能声称未做的验证已经通过。已有项目的变更使命令失效时，只更新受影响的条目；普通依赖或代码编辑不强制新建文档。

## 维护已有 uv 项目

先读取与任务相关的 `pyproject.toml`、锁文件、Python 版本、CI 和命令文档，再做目标明确的修改：

```bash
uv add requests                         # 运行依赖
uv add --dev pytest ruff                # dev 依赖组
uv add --group lint ruff                # 其他依赖组
uv remove requests
uv sync                                 # 同步项目环境
uv run pytest                           # 使用项目环境运行
uv lock --upgrade-package requests      # 有目的地更新单个依赖
uv export --format requirements-txt --output-file requirements.txt
```

这些是操作示例，不是固定依赖清单。`uv run` 默认检查锁定和同步；只使用现有环境时可用 `--no-sync`。

开发工具放在 `[dependency-groups]`，用 `uv sync --group lint` 安装相应组。`--extra` 对应 `[project.optional-dependencies]` 中供消费者选择的可选功能，二者不要混淆。

可安装包的 CLI 入口使用 Python callable：

```toml
[project.scripts]
myapp = "myapp.cli:main"
```

安装项目后运行 `uv run myapp`。测试与 lint 直接运行 `uv run pytest`、`uv run ruff check .`；uv 没有供任意 shell 命令别名使用的 `[tool.uv.scripts]`。

CI 通常用 `uv sync --locked`，再运行 `uv run --locked pytest` 等既定检查。`--locked` 在锁文件与声明不一致时失败；`--frozen` 跳过一致性检查，只在确实需要该行为时使用。

提交 `pyproject.toml` 和项目的 `uv.lock`，忽略 `.venv/`。`requires-python` 声明支持范围，`.python-version` 选择本地解释器；按部署与依赖约束选择版本，不把教程中的版本当作升级目标。只运行与改动相关且项目实际具备的检查。

## 查证入口

命令或配置有疑问时先看已安装版本的 `uv <command> --help`，再查官方文档：

- [项目配置](https://docs.astral.sh/uv/concepts/projects/config/)
- [依赖与依赖组](https://docs.astral.sh/uv/concepts/projects/dependencies/)
- [锁定与同步](https://docs.astral.sh/uv/concepts/projects/sync/)
- [单文件脚本](https://docs.astral.sh/uv/guides/scripts/)
