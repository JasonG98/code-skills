# Skills 现代化调研与改造记录

调研日期：2026-10-12。范围是本技能源码库，重点是 `vibe-to-arch`，同时处理与其目标直接冲突的 Python 指导。没有审计用户其他业务项目，因此不能断言那些项目的膨胀由 TDD 单独造成。

## 结论

这里最需要更新的是决策方式，而不是套用更复杂的目录。技能应给模型明确的目标、非显然约束、必要背景和验收依据，并允许它自行决定局部实现。减少测试维护成本需要区分有价值的行为保护与实现耦合，不能简单减少测试数量。

## 官方依据

| 来源 | 官方建议的要点 | 本项目采用的做法 |
|---|---|---|
| [OpenAI：Rethinking skills and prompts for GPT-6 Astra](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)，2026-09-11 | 收窄描述、渐进披露，重新检查固定流程和全仓阅读要求 | 入口只保留触发、判断、验收；删除强制三阶段和多轮确认 |
| [Anthropic：Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)，动态文档 | 默认模型已具备能力；按任务脆弱性调整自由度 | 删除通用编程教材，保留个人偏好和风险相关约束 |
| [Anthropic：Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)，2025-09-29 | 在过细流程与模糊提示之间取平衡；按需取得上下文 | 沿真实调用链阅读，仅在需要时读测试或迁移参考 |
| [Anthropic：Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)，2024-12-19 | 从能工作的简单方案开始，需要时再增加复杂度 | 不为了四个技能引入插件构建、编排框架或多套源码 |
| [OpenAI：Testing Agent Skills Systematically with Evals](https://developers.openai.com/blog/eval-skills)，2026-01-22 | 用可观测结果、触发场景和负例评估技能 | 保存场景、对照观察和隔离执行结果，不把格式校验当行为证明 |
| [Agent Skills specification](https://agentskills.io/specification)，动态规范 | `SKILL.md` 的名称和描述必需；脚本、参考和资源可选 | 每个技能自包含，通用结构兼容两个宿主 |

这些来源不规定唯一的“最新仓库目录”，也没有给出 Python 项目的理想测试/源码比例。下面的结构与测试取舍是针对本项目的工程判断，不是官方认证模板。

## 旧版检查结果

旧版可从改造前提交 `fdb79f7` 追溯。

| 位置 | 观察 | 影响与处理 |
|---|---|---|
| `vibe-to-arch/SKILL.md` | 描述涵盖新项目、vibe coding、系统设计等宽泛场景 | 普通任务也可能被导入重建流程；现在限定已有项目的维护痛点 |
| `phase2-graduate.md` | 五项检查必须全部通过；要求读全部原型代码，确认 SPEC 后从头开始 | 稳定项目的小整理也产生重新提炼需求与审批；改为读取相关证据 |
| `phase3-rebuild.md` | 反复停下确认，默认重写，偏向先基础设施后业务 | 造成流程与中间层增长；改为可交付切片和范围内自主执行 |
| 旧阶段规则 | 以一句话描述职责、默认丢弃 UI/脚本等方式决定拆分和重写 | 依据与维护收益脱节；改用实际耦合和兼容契约 |
| `python-coding` 及参考 | 函数 50/60 行阈值不一致，参数超过 5 个建议数据类，大量模式教材 | 鼓励机械拆分和额外封装；保留判断依据与个人风格 |
| `skills/scripts/code_analyzer.py` | 无技能引用的示例工具，硬编码长度和参数阈值，遗漏 async 函数 | 删除示例，不将其升级成另一套质量框架；使用项目已有检查工具 |
| `python-project/SKILL.md` | `[tool.uv.scripts]` 作为任务别名，dev 组与 extra 混淆 | 按 uv 文档改为真实 CLI 入口、dependency-groups 与直接运行命令 |
| 仓库根目录 | 没有用途、安装、维护说明 | 新增简短 README、共用约定、结构检查与评估目录 |

uv 的依据是 [项目配置](https://docs.astral.sh/uv/concepts/projects/config/)、[依赖组](https://docs.astral.sh/uv/concepts/projects/dependencies/) 和 [锁定同步](https://docs.astral.sh/uv/concepts/projects/sync/)。`--locked` 校验声明与锁文件一致，`--frozen` 跳过该校验，不能视作同义词。

## 结构选择

保留 `skills/<name>/` 作为源码库。每个目录可以单独安装；`references/` 放按需知识，技能自己的 `scripts/` 放运行工具，`agents/openai.yaml` 只用于 Codex 界面信息。

仓库维护脚本放根目录 `scripts/`，调研放 `docs/`，行为评估放 `evals/`。这些内容不随技能安装，也不应被每次调用加载。`CLAUDE.md` 导入同一份 `AGENTS.md`，避免维护两套不同约定。

本地发现位置与源码布局是两件事。当前 [Codex](https://learn.chatgpt.com/docs/build-skills) 使用 `.agents/skills`，而 [Claude Code](https://code.claude.com/docs/en/skills) 使用 `.claude/skills`；README 提供将两者链接到同一源码的方法。若以后需要公开发布、版本化安装或 MCP 集成，再增加对应宿主的插件包装。

## 新版 vibe-to-arch 的设计

以具体维护痛点作为入口，允许“无需改动”作为结论。默认选择删除、内联、合并或局部迁移；用户明确要求或成本证据支持时才重写。核心指导跨语言，Python 示例独立放置。

测试策略围绕真实行为：复用已有覆盖，独有边界先迁移再删旧测试，保留授权顺序、幂等和事务等有效交互契约。纯重构保持已有测试通过，不要求重复证明相同行为。新行为与缺陷修复仍可采用 TDD，明确的项目流程仍须遵守。

重构结束时清理它直接废弃的路径、配置与依赖；真实外部消费者尚未迁移时保留兼容并写明退出条件。验收标准是修改成本降低和契约保持，行数下降只用于观察文档体积。

## 改造规模与验证边界

按 Markdown 的 `splitlines()` 统计（包含空行）：

| 范围 | 旧版行数 | 新版行数 |
|---|---:|---:|
| vibe-to-arch 主文件及参考 | 548 | 156 |
| python-coding 主文件及参考 | 2,017 | 71 |
| python-project | 145 | 62 |
| 全部安装包内 Markdown | 2,863 | 444 |

这是文档体积变化，不是 token、速度或质量收益的测量。增加的仓库说明和评估记录位于安装包之外。

本轮做了结构校验、无技能/旧版/新版的单次对照、边界场景走查和一个 Python 隔离项目的实际执行。结果与局限见 [验证记录](../evals/2026-10-12-results.md)。尚未在 Claude Code 或多个模型版本上重复采样，不能由此宣称跨模型效果已被证明。

## 后续使用时的注意点

本机已安装的 `~/.agents/skills/` 中存在独立旧副本，Claude 的相关链接指向这些副本。本次只改源码库，没有改全局安装；需要比较并同步后，新版才会用于其他项目。

同时加载的流程技能也会影响结果。本会话可用的 `using-superpowers`、`brainstorming`、`test-driven-development` 等带有强触发、审批或测试先行要求。它们在相应任务中可能有价值，但与本技能的按需工作流叠加时，仍可能增加过程成本。建议按任务选用并核查冲突，不把“全部常开”当成默认优化；本次没有修改这些第三方技能或全局配置。
