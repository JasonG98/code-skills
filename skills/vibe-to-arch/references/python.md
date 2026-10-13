# Python 项目的最小结构

仅在 Python 项目需要目录或边界调整时读取。先尊重现有打包方式、框架和 Python 版本。

单文件工具可以继续单文件；包含可安装包的项目可采用以下起点。它是示例，不是每个项目都要生成的模板：

```text
pyproject.toml
src/myapp/
    __init__.py
    cli.py           # 或 web / GUI 入口
    export.py        # 一个真实业务能力
    storage.py       # 存储边界确实需要隔离时再建
tests/
    test_export.py
    test_storage.py
```

包的安装与导入边界有意义时使用 `src/`；稳定的 flat layout 无须为目录外观迁移。能力增多后按业务变化聚合，再在实际边界内分层。

优先函数和模块。数据在多处以稳定语义传递时考虑 dataclass；要表达实际存在的可替换边界时考虑 Protocol。没有实际需求时，不为每个功能创建 service、repository、interface、factory、DTO 和 manager。

把 I/O 与复杂的纯计算适当分开，可以降低验证成本。简单流程中，直接传入路径、连接或 callable 往往已经足够，无需依赖注入框架。

**例子：** `ExportController → ExportService → ExportManager → CsvWriter` 中若两层只转发参数，可检查调用方后内联为入口调用 `export_csv(...)`。仍保留有业务意义的事务、编码与错误语义。复用公开导出行为测试；私有调用顺序测试按其保护的真实行为迁移。

格式、lint 和类型检查沿用 `pyproject.toml` 与 CI 中已有配置。修复目标模块即可，不把一次架构整理变成全仓格式化、Python 升级或包管理器迁移。
