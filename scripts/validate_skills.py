#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["PyYAML==6.0.3"]
# ///
"""检查本仓库的 skill 元数据、文件引用和 Python 语法, 不评判模型行为."""

import argparse
import ast
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml


def validate(root: Path) -> list[str]:
    """返回结构错误, 空列表表示此检查范围内未发现问题."""
    errors = []
    skills = root / "skills"
    manifests = sorted(skills.glob("*/SKILL.md"))
    if not manifests:
        return [f"{skills}: no skills found"]
    for directory in sorted(skills.iterdir()):
        if directory.is_dir() and not (directory / "SKILL.md").is_file():
            errors.append(f"{directory}: missing SKILL.md; move repository tools outside skills/")
    for manifest in manifests:
        content = manifest.read_text(encoding="utf-8")
        match = re.match(r"\A---\n(.*?)\n---(?:\n|$)", content, re.DOTALL)
        if not match:
            errors.append(f"{manifest}: missing YAML frontmatter")
            continue
        try:
            metadata = yaml.safe_load(match.group(1))
        except yaml.YAMLError as error:
            errors.append(f"{manifest}: invalid YAML: {error}")
            continue
        if not isinstance(metadata, dict):
            errors.append(f"{manifest}: frontmatter must be a mapping")
            continue
        name = metadata.get("name")
        if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
            errors.append(f"{manifest}: invalid name")
        elif len(name) > 64 or name != manifest.parent.name:
            errors.append(f"{manifest}: name must match directory and be <=64 characters")
        description = metadata.get("description")
        if not isinstance(description, str) or not 1 <= len(description.strip()) <= 1024:
            errors.append(f"{manifest}: description must contain 1..1024 characters")
        if not content[match.end():].strip():
            errors.append(f"{manifest}: empty instructions")
        for document in manifest.parent.rglob("*.md"):
            text = document.read_text(encoding="utf-8")
            # 仅检查本仓库使用的行内 Markdown 链接, 忽略示例代码和锚点.
            prose = re.sub(r"(?ms)^```[^\n]*\n.*?^```\s*$", "", text)
            for target in re.findall(r"\[[^\]\n]+\]\(([^)\s]+)\)", prose):
                url = urlsplit(target)
                if url.scheme or url.netloc or not url.path:
                    continue
                resource = (document.parent / unquote(url.path)).resolve()
                if not resource.is_relative_to(manifest.parent.resolve()):
                    errors.append(f"{document}: link escapes skill bundle: {target}")
                elif not resource.exists():
                    errors.append(f"{document}: missing resource: {target}")
    for script in [*skills.rglob("*.py"), *(root / "scripts").rglob("*.py")]:
        try:
            ast.parse(script.read_text(encoding="utf-8"), filename=str(script))
        except SyntaxError as error:
            errors.append(f"{script}:{error.lineno}: {error.msg}")
    return errors


def main() -> int:
    """从任意工作目录检查指定仓库, 出错时返回非零状态."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = validate(args.root.resolve())
    if errors:
        print("\n".join(errors))
        return 1
    count = len(list((args.root / "skills").glob("*/SKILL.md")))
    print(f"Validated {count} skills: metadata, local resource links, Python syntax.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
