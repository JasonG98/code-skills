---
name: python-coding
description: Apply personal Python coding and review conventions when writing or reviewing Python code. Follow existing project configuration and supported Python versions first.
---

# Python Coding

已有项目约定优先。没有约定时，采用下面的个人偏好；不为统一风格扩大修改范围。

## 实现选择

- 先检查 Python 支持版本和 `pyproject.toml`，使用兼容的类型语法和已有检查工具。
- 让类型标注表达公共边界和非显然的数据约束；不为了类型形式增加无实际用途的封装。
- 函数、模块和直接调用足够时就使用它们。重复业务规则、真实替换需求或状态生命周期才是提取抽象的依据。
- 函数行数、参数数量是审查线索，不是硬性拆分条件。参数形成稳定概念时才考虑 dataclass；实际存在可替换边界时才考虑 Protocol。
- 资源生命周期与失败语义要明确。捕获能够处理的异常，保留调用方需要的错误信息，避免静默吞错和导入时执行外部 I/O。

## 个人风格

无现有约定时，使用 4 空格缩进、120 字符行宽和中文说明。注释与 docstring 使用英文半角标点，中英文之间留空格。让格式化工具处理机械规则。

文档解释契约、约束和非显然原因。公共 API 或复杂行为需要说明时使用 Google 风格；清楚的短函数无需复述签名。完整示例见 [文档风格](references/style-guide.md)，仅在写文档说明时读取。

## 验证与审查

沿用项目已有的测试、lint 和类型检查命令，按影响范围运行。行为已有保护时复用测试；增加新行为或修复缺陷时补能发现该回归的最小测试。测试真实行为，替身主要用于外部边界。

正式审查时读取 [审查重点](references/code-review-checklist.md)，优先报告可证明的问题。项目出现持续的架构或测试维护成本时可使用 `vibe-to-arch`；普通实现不需要加载架构工作流。
