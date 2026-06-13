---
name: vibe-to-arch
description: >
  A full project lifecycle methodology covering two phases: fast exploration (vibe coding) 
  followed by systematic rebuild (clean architecture). Use this skill whenever the user 
  mentions starting a new project, wants to explore an idea without committing to architecture,
  says "MVP is done" or "validation complete" and is thinking about a refactor or rebuild,
  asks how to approach a large-scale refactor, wants to transition from messy prototype to 
  clean system, mentions "vibe coding" or exploratory development, or asks about system design
  after building a working prototype. This skill applies even when the user doesn't explicitly
  ask for it — if they're showing signs of being between exploration and architecture, step in.
---

# Vibe-to-Arch

## Core Philosophy

Architecture-first development is a bet on knowing what you're building before you've built it.
That bet rarely pays off. The better model:

**Phase 1 — Explore:** Vibe code your way to understanding. Ship fast, break things, learn faster.
The code is a side effect; the real output is knowledge.

**Phase 2 — Graduate:** When exploration converges, stop. Distill what you learned.
Don't carry vibe-code assumptions into the new system.

**Phase 3 — Rebuild:** Now that you know what you're building, build it right.
First principles → clean architecture → systematic implementation.

The key insight: **vibe code is the best requirements document ever written.**
It's concrete, executable proof of what the system actually needs to do.
The rebuild isn't a failure — it's the payoff for good exploration.

---

## Stage Router

Before doing anything, identify which phase the user is in.

Ask (or infer from context) two questions:

1. "Have you validated the core functionality — do you know what this system needs to do?"
2. "Can you describe the system's purpose, inputs, outputs, and constraints in one paragraph without referring to the code?"

| Situation | Go to |
|-----------|-------|
| Starting fresh / exploring an idea | `phase1-explore.md` |
| Prototype works, considering cleanup | `phase2-graduate.md` (don't skip this) |
| Graduation confirmed, ready to rebuild | `phase3-rebuild.md` |
| Both questions answered "yes" | `phase2-graduate.md` → `phase3-rebuild.md` |
| Either question answered "no" | `phase1-explore.md` |

**Never jump from Phase 1 directly to Phase 3.**
Phase 2 exists specifically to prevent carrying vibe-code assumptions into the new system.

---

## Reference Files

Load only the file for the current phase — not all three upfront:

- `phase1-explore.md` — Strategic exploration: how to vibe code with intent
- `phase2-graduate.md` — Graduation: assessing readiness + spec extraction
- `phase3-rebuild.md` — Rebuild: first principles → architecture → implementation

---

## Principles (Always Apply Across All Phases)

**1. Wrong fast beats right slow in Phase 1.**
Premature correctness is just procrastination with good posture.

**2. Knowledge has an expiration date.**
The gap between Phase 1 and Phase 3 should be days, not months.
Context decays. LEARNINGS.md exists to fight this.

**3. Spec extraction before architecture.**
Phase 3 starts by distilling what Phase 1 proved — not by designing from scratch.
The vibe code is a research artifact, not a scaffold to build on.

**4. Stop points are mandatory in Phase 3.**
This is a collaborative process. Claude surfaces decisions; humans confirm them.
No unilateral architecture choices, no silent workarounds.

**5. Strategic messiness.**
Not all Phase 1 code deserves equal care.
Core logic and data models: leave traces.
Scripts, UI, experiments: throw away freely.

**6. Rebuilds can be partial.**
Not every refactor needs to be a full teardown.
A single module can be rebuilt while others remain.
This skill applies at any granularity.
