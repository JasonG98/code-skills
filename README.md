# Personal Agent Skills

用于 Codex 和 Claude Code 的个人技能库，以 Python 开发为主。架构整理方法适用于其他语言。

## 技能

| Skill | 适用场景 |
|---|---|
| [vibe-to-arch](skills/vibe-to-arch/SKILL.md) | 已有项目的架构、代码或测试维护成本持续增加 |
| [converge-to-core](skills/converge-to-core/SKILL.md) | 将 AI/ML 实验仓库精简到核心算法与流程，允许不兼容旧数据和 checkpoint |
| [python-coding](skills/python-coding/SKILL.md) | Python 实现与审查中的个人约定 |
| [python-project](skills/python-project/SKILL.md) | uv 项目的环境、依赖、打包与 CI |
| [flat-diagram-style](skills/flat-diagram-style/SKILL.md) | 跨领域扁平图解风格，按需求选择格式；附 PNG 工具 |
| [daily-report](skills/daily-report/SKILL.md) | 从本机 Claude Code 历史生成日报；需要 Python 3 和历史记录 |
| [think](skills/think/SKILL.md) | 第一性原理、质疑提问本身、二阶影响、跨领域、反方视角 |
| [align](skills/align/SKILL.md) | 开局先问清目标，再给三版方案供选择 |
| [retro](skills/retro/SKILL.md) | 复盘近期 Bug 与返工，找共同根因并沉淀成规则或自动化 |

`vibe-to-arch` 不会因普通修复或新建项目自动要求重建。它优先找具体维护障碍，复用现有行为测试，然后执行一个可验证的简化切片。

## 仓库结构

```text
skills/
  <name>/
    SKILL.md             # 必需：触发范围与核心判断
    references/          # 按需读取的资料
    scripts/             # 技能运行必需的工具（如有）
    agents/openai.yaml   # Codex 界面元数据（如有）
scripts/                 # 维护本仓库的工具
evals/                   # 触发、行为和边界场景
docs/                    # 调研与设计依据
AGENTS.md                # 仓库维护约定
CLAUDE.md                # 导入同一份约定
```

这是技能源码库；`skills/` 不等于工具的自动发现目录。每个子目录独立安装，保留一份源码。资源按实际需要创建，不为空目录补模板。没有 MCP 或公开插件分发需求，因此暂不增加插件清单和构建系统。

## 安装到本机

Codex 使用 `~/.agents/skills/<name>/`，Claude Code 使用 `~/.claude/skills/<name>/`。[Vercel `skills` CLI](https://github.com/vercel-labs/skills) 可一次装到两者，并从本仓库的 `skills/` 自动发现技能。

在仓库根目录运行以下命令。示例只安装 `vibe-to-arch`；用 `--skill` 重复指定或写 `'*'` 安装全部。

```bash
bunx skills@latest add https://github.com/JasonG98/code-skills \
  --skill vibe-to-arch \
  -g -a claude-code -a codex -y
```

`-g` 装到用户级（去掉则装进当前项目的 `.claude/skills/`）。已安装的技能用 `bunx skills@latest update -g` 更新，`bunx skills@latest ls -g` 查看，`bunx skills@latest remove -g <name>` 卸载。

远程安装会记录 commit，改完仓库要先推送再 `update`。本机调试可直接用本地路径，但那是复制而非链接，同样需要 `update` 才会同步。不要同时在多个发现目录放不同版本的同名技能。

项目级安装则使用目标项目的 `.agents/skills/<name>/` 和 `.claude/skills/<name>/`；需要团队共享时，提交可移植的文件，而非本机绝对路径链接。

## 使用

Codex 示例：

```text
用 $vibe-to-arch 检查当前项目最贵的维护热点，保留功能与公开接口，
先完成一轮最值得的简化，说明删减依据和验证结果。
```

Claude Code 使用 `/vibe-to-arch`。只要审计时补充“只输出建议，不修改文件”。

这里的“精简”以降低修改成本为目标。TDD 用来保护明确行为；已有测试足够的纯重构复用保护，删测需解释原有保护的去向，不能通过削弱契约让数字变小。

## 维护与验证

```bash
uv run scripts/validate_skills.py
```

验证器使用脚本内声明的 PyYAML 依赖，无需为技能库创建 Python 应用项目。它检查名称、描述、技能内行内链接与 Python 语法，不访问外部链接，不验证 Markdown 锚点，也不能证明模型表现。

修改重要工作流后，用 [行为场景](evals/vibe-to-arch.md) 检查触发和决策；实际记录见 [本轮验证](evals/2026-10-12-results.md)。模型升级后可复跑失败风险最高的场景。

官方依据、旧版问题和本轮取舍见 [调研记录](docs/2026-10-12-skill-modernization.md)。
