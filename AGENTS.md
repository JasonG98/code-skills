# Repository guidance

## Product

Personal Agent Skills source library for Codex and Claude Code. Not a Python application: no package, no test suite, no CI.

## Boundaries

- Do not install, update, or overwrite anything under `~/.claude/skills/` or `~/.agents/skills/` as part of repository maintenance. Editing this repo does not touch installed copies.
- Do not commit, push, or publish without explicit request.

## Conventions

- `skills/<name>/` is a portable bundle. Each skill must work standalone: no imports from sibling skills, no references to repo-level `docs/` or `evals/`.
- `SKILL.md` covers task selection, decisions, constraints, and output. Conditional detail goes in linked `references/`; add scripts only for useful deterministic work.
- Repository maintenance tools live in root `scripts/`. Research and behavioral evals live in `docs/` and `evals/`, outside installed bundles.
- Keep fixtures and generated traces out of `skills/`. Add regression cases for demonstrated failures, not imagined edge cases.
- Skills must not turn routine edits into mandatory architecture, TDD, documentation, or approval ceremonies. Preserve the user's scope, authorization, and existing project conventions.

## Done

- Run `uv run scripts/validate_skills.py` after structural changes. It checks metadata, inline local resource links, and Python syntax; it does not check behavioral quality or every Agent Skills extension.
- For material workflow changes, run representative requests plus a negative control and record what actually ran. Use isolated temporary projects for execution trials.
- Edit files directly and iterate until validation is clean. Do not stop for review unless the change touches Boundaries.

## Docs

- `docs/2026-10-12-skill-modernization.md`: design rationale and prior trade-offs. Read before restructuring `SKILL.md` conventions.
- `evals/`: trigger and boundary scenarios per skill. Re-run the riskiest after model upgrades.
