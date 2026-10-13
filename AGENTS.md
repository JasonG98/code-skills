# Repository guidance

This repository authors reusable skills; it is not a Python application.

- `skills/<name>/` is the portable source bundle. Each skill must work without sibling skills or repository docs being installed.
- Keep `SKILL.md` focused on task selection, decisions, constraints, and output. Put conditional detail in linked `references/`; add scripts only for useful deterministic work.
- Repository maintenance tools live in root `scripts/`. Research and behavioral evals live in `docs/` and `evals/`, outside installed bundles.
- Preserve the user's scope, authorization, and existing project conventions. Do not turn routine edits into mandatory architecture, TDD, documentation, or approval ceremonies.
- Validate structural changes with `uv run scripts/validate_skills.py`. This checks metadata, inline local resource links and Python syntax, not behavioral quality or every Agent Skills extension.
- For material workflow changes, exercise representative requests and a negative control; record what actually ran. Use isolated temporary projects for execution trials.
- Keep fixtures and generated traces out of installed skills. Add regression cases for demonstrated failures, not every imagined edge case.
- Editing this repository does not update separately installed copies. Do not overwrite user-level skill directories as part of repository maintenance.
