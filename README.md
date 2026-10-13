# Personal Agent Skills

用于 Codex 和 Claude Code 的个人技能库，以 Python 开发为主。架构整理方法适用于其他语言。

## 技能

| Skill | 适用场景 |
|---|---|
| [vibe-to-arch](skills/vibe-to-arch/SKILL.md) | 已有项目的架构、代码或测试维护成本持续增加 |
| [python-coding](skills/python-coding/SKILL.md) | Python 实现与审查中的个人约定 |
| [python-project](skills/python-project/SKILL.md) | uv 项目的环境、依赖、打包与 CI |
| [flat-diagram-style](skills/flat-diagram-style/SKILL.md) | 跨领域扁平图解风格，按需求选择格式；附 PNG 工具 |
| [daily-report](skills/daily-report/SKILL.md) | 从本机 Claude Code 历史生成日报；需要 Python 3 和历史记录 |

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

Codex 使用 `~/.agents/skills/<name>/`，Claude Code 使用 `~/.claude/skills/<name>/`；两者都支持技能目录软链接。[Codex 文档](https://learn.chatgpt.com/docs/build-skills) · [Claude Code 文档](https://code.claude.com/docs/en/skills)

在仓库根目录运行以下命令，为所需技能建立链接。示例只安装 `vibe-to-arch`；可按需替换名称。

```bash
skills_repo="$(pwd)"
skill_name="vibe-to-arch"
for skills_target in "$HOME/.agents/skills" "$HOME/.claude/skills"; do
  mkdir -p "$skills_target"
  if [ -e "$skills_target/$skill_name" ] || [ -L "$skills_target/$skill_name" ]; then
    printf '保留已有安装，请先检查：%s\n' "$skills_target/$skill_name"
  else
    ln -s "$skills_repo/skills/$skill_name" "$skills_target/$skill_name"
  fi
done
```

已有实体副本需先比较、备份，再换成指向此仓库的链接；这段命令不会更新旧副本。不要同时在多个发现目录放不同版本的同名技能。仓库移动后需更新链接。Windows 或不支持软链接的环境可复制整个技能目录，但要自行同步更新。

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
