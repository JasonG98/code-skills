# 2026-11-20 python-project 重构验证

对象：`skills/python-project/` 的任务分流、初始化约束、工具配置参考和项目命令文档规则。基准提交：`def672d`；本机 uv：0.13.9（macOS arm64）。

本次使用独立子代理各执行一次新项目和已有项目场景，属于小样本定性检查，不证明自动触发效果或跨模型稳定性。所有执行文件均位于隔离临时目录，未修改用户级技能副本。

## 结构与静态检查

- `uv run scripts/validate_skills.py`：9 个技能通过元数据、本地资源链接和 Python 语法检查。
- 使用 Python 3.13 的 `tomllib` 解析参考文件中的 4 个 TOML 块：全部有效。
- 搜索 `myapp train`、`checkpoint`、`ONNX`、`viser`：技能包中无这些特定项目命令示例。
- `git diff --check -- skills/python-project`：通过。

## 新项目场景

请求：在隔离目录用 uv 新建可安装 CLI，建立开发检查和项目命令文档。

执行代理在 `/tmp/python-project-demo-cli-eval.R9piAX/demo_cli` 完成以下实际流程：

- `uv init --package --vcs none` 生成初始项目和 `pyproject.toml`。
- `uv add --dev pytest ruff pyright` 安装开发工具，`uv sync --locked` 成功。
- 配置按项目实际的 `requires-python = ">=3.9"` 使用 `py39` / `3.9`，目录只包含真实存在的 `src/` 和 `tests/`。
- 新增测试只调用生成的 CLI `main()` 并验证真实问候输出，没有添加 ML 功能。
- `uv run demo-cli` 成功；Ruff 静态检查、Ruff 格式检查、Pyright 和 pytest 均通过，pytest 为 1 项通过。
- `AGENTS.md` 只含六条已执行的同步、CLI 和检查命令，无 train、checkpoint、ONNX 等内容。

主代理随后检查实际 `pyproject.toml`、测试和 `AGENTS.md`，并用 `uv run --no-sync` 重新运行四项检查：Ruff 静态检查通过、格式检查通过、Pyright 0 errors / 0 warnings、pytest 1 项通过。

## 已有项目与负向控制

请求：已有 uv flat-layout 项目只添加 requests，不做其他改造。样本已有自定义 Ruff 行宽 88 和自定义 `AGENTS.md`。

- 执行 `uv add requests` 后，依赖声明与 `uv.lock` 更新，普通运行及 `--locked` 环境中的 requests 导入均成功。
- 未运行 `uv init`，未创建 `src/`，未添加 Pyright、Pytest、dependency group 或 build-system。
- 自定义 Ruff 配置、`AGENTS.md` 和源码保持不变。主代理抽查确认 flat layout 仍在且行宽配置未变。

另一个带 `[tool.poetry]` 的非 uv 样本用于负向走查。本机没有 Poetry，执行代理记录无法完成对应依赖维护并停止，没有改用 uv、生成 `uv.lock`、创建 `.venv` 或改写项目文件。主代理确认该目录仍只有原来的 `pyproject.toml`、源码和 `AGENTS.md`。

## 限制

- 每个行为场景只执行一次，执行代理读取了完整技能；这不构成自动触发或跨模型稳定性的证据。
- 没有实际解析 tuna 镜像或下载 CUDA wheel，没有运行 GPU/长耗时命令。
- 没有执行分发构建、跨平台验证，也没有修改单独安装的用户级技能副本。
