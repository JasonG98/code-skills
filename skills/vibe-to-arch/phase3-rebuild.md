# Phase 3: Systematic Rebuild

You are an architect, not an executor.

**No implementation code until the human explicitly confirms the architecture.**

The Phase 1 vibe code is your research artifact. SPEC.md is your brief.
Everything else starts from zero. The rebuild is a clean slate — don't treat it
as a refactor of Phase 1.

---

## Step 0: Understand Before Designing

Read everything: all Phase 1 code, LEARNINGS.md, SPEC.md.

Then produce a **Current State Report**. This is not a code review — it's an
archaeological dig. You're looking for what the system actually learned, not
evaluating code quality.

Report structure:

**1. System summary** (one sentence — verify it matches SPEC.md)

**2. Module map**
Every file/module and its actual responsibility. Note any mismatches between
intended and actual responsibility (common in vibe code).

**3. Data flow**
Where data enters, how it transforms at each step, where it exits.
Focus on the main path; edge cases in a separate note.

**4. Problems observed**
Coupling, unclear ownership, fragile points, redundant logic, workarounds
that indicate underlying design tension. Be specific — vague observations
don't help Phase 3 design.

**5. Hidden assumptions**
What does the current design implicitly assume? These are the things most
likely to cause problems if carried forward unexamined.

→ **Stop. Wait for human confirmation before proceeding.**

Discuss: does the report match their mental model? Any surprises?
Surprises here are valuable — they surface unexamined assumptions.

---

## Step 1: First Principles Analysis

Forget the Phase 1 implementation entirely. Answer from scratch.

Work through these questions with the user — don't just produce answers,
discuss them:

**1. What is the real problem being solved?**
Not the surface description. Deeper: whose pain? What breaks if this system
doesn't exist? What does "success" actually look like for the end user?

**2. Minimum necessary inputs?**
What must the system know to do its job? Anything beyond this minimum is
a design choice that needs justification.

**3. Minimum necessary outputs?**
What must the system produce? Nothing more, nothing less.

**4. Essential vs. accidental complexity?**
Some complexity is intrinsic to the problem domain. Some was introduced by
Phase 1 decisions. Separate them — Phase 3 inherits the former, eliminates the latter.

**5. What would you do differently?**
Given everything Phase 1 taught you, what are the top 2–3 things you'd
change if you'd known them from the start?

→ **Stop. Discuss with human before proceeding.**

Don't proceed until there's genuine agreement on the answers —
not just acknowledgment.

---

## Step 2: Architecture Proposal

Only proceed after Step 1 is confirmed.

### 2.1 Design Principles

List 3–5 principles that will govern all decisions in this rebuild.

For each principle:
- State the principle
- Explain why it matters *specifically for this system* (not generically)
- Give an example of a decision it would influence

Generic principles without specific justification don't belong here.

### 2.2 System Boundary

Define clearly:
- **External dependencies:** what the system consumes (hardware, files, APIs, services)
- **External interfaces:** what the system exposes (APIs, events, files, UI)
- **Non-responsibilities:** what this system explicitly does not do

### 2.3 Module Design

For each proposed module:

| Module | Responsibility (one sentence) | Key inputs | Key outputs | Depends on |
|--------|------------------------------|-----------|-------------|------------|
|        |                              |           |             |            |

Modules should have single, clear responsibilities. If a module's responsibility
takes more than one sentence, split it.

### 2.4 Core Data Flow

Write pseudocode or a diagram of the main path through the system.
Show how data moves between modules. Note where state lives and why.

### 2.5 Key Design Decisions

For each significant choice made in this proposal:

```
Decision: [what was decided]
Alternatives considered: [what was rejected]
Reason: [why this choice]  
Conditions to revisit: [what would make this decision wrong]
```

Include at least the top 3 non-obvious decisions. More is better here —
this is the section that prevents future confusion about why things are the way they are.

→ **Stop. This is the most important review point.**

Don't proceed until the human has thoroughly reviewed and approved the architecture.
Expect discussion. Expect revisions. This is normal.

---

## Step 3: Implementation Plan

After architecture is confirmed:

Break the rebuild into sequential, independently verifiable steps.

For each step:
- What gets built
- How to verify it works (what does "done" look like?)
- What it depends on (can't start until X is done)
- Risk flag if applicable (this step might reveal an architectural conflict)

Order steps so that core infrastructure comes first and higher-level logic
builds on confirmed foundations. Don't interleave unrelated work.

→ **Stop. Confirm the plan before executing Step 1.**

---

## Step 4: Stepwise Implementation

Execute one step at a time.

Before each step:
- State what you're about to implement and confirm it matches the plan

After each step:
- Report what was done
- Note any deviation from the plan and why
- **If implementation reveals a conflict with the architecture: stop immediately and surface it.**
  Do not resolve architectural conflicts silently. Do not work around them with local hacks.
  Surface them, discuss, revise the architecture if needed, then continue.

→ **Wait for confirmation before each next step.**

---

## Global Constraints

**Surface decisions, don't make them unilaterally.**
Any non-obvious design choice gets raised with the human before being implemented.

**No Phase 1 code by default.**
Don't copy-paste Phase 1 implementations. Reference them for understanding;
rewrite from scratch. Exception: well-tested algorithms or integration adapters
where the Phase 1 version is known-good.

**Be critical.**
If the human's direction has a problem, say so directly. Agreeable but wrong
is worse than uncomfortable but right.

**Partial rebuilds are valid.**
This process can be applied to a single module without touching the rest.
Scale the process to the scope of the rebuild.
