# Phase 2: Graduation Assessment

**Do not skip this phase.** The most common failure mode is jumping from vibe code
directly to rebuilding — carrying unexamined assumptions, hidden complexity, and
implicit design choices into the new system.

Phase 2 has one job: distill what Phase 1 actually proved.

---

## Why This Phase Exists

Vibe code accumulates two kinds of knowledge:

- **Explicit knowledge:** what's in the code and comments
- **Tacit knowledge:** why things are the way they are, what was tried and abandoned,
  which edge cases bit you, which assumptions were wrong

The explicit knowledge transfers automatically. The tacit knowledge evaporates —
unless you extract it now, before you switch contexts.

Phase 2 is the extraction process.

---

## The Graduation Checklist

Work through all five with the user. All five must pass before proceeding to Phase 3.
If any fail, the answer isn't "close enough" — go back to Phase 1 and close the gap.

### ① Core Purpose
> "Describe what this system does in one sentence, for someone who has never seen the code."

If the answer is vague, takes multiple sentences, or describes the implementation rather
than the purpose — Phase 1 isn't done.

### ② Boundary Definition
> "What does this system explicitly NOT do? What's out of scope?"

Boundaries matter as much as capabilities. A fuzzy boundary in Phase 2 becomes sprawl in Phase 3.

### ③ Validated/Invalidated Assumptions
> "What did you believe at the start of Phase 1 that turned out to be wrong?"

If the answer is "nothing" — that's a red flag, not a sign of good planning.
Real exploration invalidates assumptions. If nothing was invalidated, you weren't learning.

### ④ Essential Complexity
> "What parts of this problem are genuinely hard? Where did you reach for workarounds?"

This identifies where Phase 3 needs the most architectural care.
Easy problems don't need architecture. Hard problems do.

### ⑤ The One-Page Test
> "Write a paragraph covering: what the system does, who or what uses it, what the
> inputs and outputs are, and what the core constraints are."

This is the final exam. If this paragraph can't be written confidently and concisely
without referring to the code — Phase 1 isn't done. Return and keep exploring.

---

## Spec Extraction

Once all five checklist items pass, extract a clean spec. This is not documentation —
it's the **source of truth for Phase 3 architecture**.

Instruct Claude to:

1. Read all Phase 1 code and LEARNINGS.md in full
2. Identify the minimum set of inputs and outputs the system must handle
3. Identify the invariants — things that must always be true regardless of input
4. Identify the failure modes the current code already handles
5. Produce `SPEC.md` using the template below

```markdown
# SPEC.md

## System Purpose
One paragraph. What does it do, for whom, and why does it matter.

## Users / Consumers
Who or what calls this system? Human users? Other services? Both?

## Core Inputs
| Input | Type | Constraints / Notes |
|-------|------|---------------------|
|       |      |                     |

## Core Outputs
| Output | Type | Guarantees |
|--------|------|------------|
|        |      |            |

## Invariants
Conditions that must always hold. These constrain the architecture.
- 

## Edge Cases (Discovered in Phase 1)
Non-obvious situations the system must handle correctly.
- 

## Failure Modes (Handled)
How the current system handles things going wrong. Keep what works.
- 

## Explicitly Out of Scope
What this system will NOT handle, and why.
- 

## Open Design Questions
Decisions Phase 3 needs to make. Don't answer them here.
- 
```

---

## After Spec Extraction

Review SPEC.md with the user. Specifically verify:

- Does the stated purpose match what the user actually wanted to build?
- Are the boundaries clear enough to make architectural decisions?
- Are the invariants real constraints, not aspirational ones?
- Do the open design questions capture actual uncertainty — or are they already answered?

Only after the user confirms SPEC.md is accurate:

1. **Archive** the Phase 1 code — don't delete it. It's a reference artifact, not a scaffold.
   Create a `phase1-archive/` directory or tag the git state.
2. **Start fresh** for Phase 3. No copy-pasting from Phase 1 code.
3. Load `phase3-rebuild.md` and begin.
