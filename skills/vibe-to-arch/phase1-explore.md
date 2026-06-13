# Phase 1: Strategic Exploration

You are in vibe coding mode. The goal is **learning, not building** — the code is a
side effect of figuring out what the system actually needs to do.

Resist the urge to design. Resist the urge to clean up. Embrace productive chaos —
but be strategic about where you put the chaos.

---

## The Strategic Messiness Framework

Apply this filter before writing any code:

| Code type | Treatment | Reason |
|-----------|-----------|--------|
| Core business logic | ⚡ Leave traces | Becomes the reference for Phase 3 design |
| Data models / schemas | ⚡ Leave traces | Shape defines everything; hard to recover later |
| Key algorithms | ⚡ Leave traces | Edge cases discovered here are gold |
| External integrations | 😐 Functional only | Just make it work, document the gotchas |
| UI / scripts / CLI | 🗑️ Throwaway | Delete freely in Phase 3 |
| Experiments / spikes | 🗑️ Throwaway | Capture the *finding*, delete the code |
| Config / infra | 😐 Functional only | Don't over-engineer, but don't make it a maze |

**"Leave traces"** means adding a one-line comment explaining *why*, not *what*.
The what is obvious from the code. The why evaporates from memory.

```python
# Polling instead of websocket — websocket latency caused false positives in early tests
# Hard-coded threshold=0.7 after empirical testing on 200 samples; see LEARNINGS.md
# Separate queue here because batch processing caused unacceptable UI lag
```

These comments are breadcrumbs for your Phase 3 self.

---

## LEARNINGS.md

Create this file at the project root **on Day 1**. This is the most important artifact
Phase 1 produces — more valuable than the code itself.

Don't write it like a log. Write it like a memo to your future self who's about to
rebuild this from scratch and needs to understand what you discovered.

```markdown
# LEARNINGS.md

## What this system actually does
(Rewrite this every few days as your understanding evolves)

---

## Validated assumptions
Things we believed that turned out to be true.
- 

## Invalidated assumptions  
Things we believed that turned out to be wrong. These matter most.
- 

## Surprising discoveries
Things we didn't expect to find.
- 

---

## Design decisions
| Decision | Alternatives considered | Reason chosen |
|----------|------------------------|---------------|
|          |                        |               |

## Known intentional shortcuts
Technical debt we chose deliberately and why.
- 

## Edge cases discovered
Things the system needs to handle that weren't obvious at the start.
- 

## Open questions
Things Phase 3 needs to decide.
- 
```

### Capture rhythm

Update LEARNINGS.md at these moments — not constantly, not never:

- Something didn't work the way you expected → log the surprise
- You made a non-obvious design choice → log the reasoning
- You finished a major feature → update "what this system does"
- A previous assumption turned out to be wrong → move it to "invalidated"
- You found a non-obvious edge case → log it immediately

**Rule of thumb:** if you'd need to reconstruct the reasoning from code archaeology
in Phase 3, write it down now.

---

## What Good Phase 1 Execution Looks Like

**Do:**
- Spike freely — try multiple approaches, keep the one that works
- Let the data model evolve; don't lock it in early
- Ship to a real environment early, even if rough
- Let failure modes surface naturally; don't over-engineer error handling
- Prioritize getting all major features to "working" over getting any single feature to "polished"

**Don't:**
- Write tests for throwaway code (waste of Phase 1 time)
- Refactor for elegance (that's Phase 3's job)
- Design for extensibility you don't know you need yet
- Let Phase 1 drag on because "just one more feature"

---

## Phase 1 Completion Signal

You're done with Phase 1 when:

- All core features are working (not polished, just working)
- The surprises have stopped — you're not learning new things about the problem domain
- You could explain the system to someone new without referring to the code
- The "open questions" in LEARNINGS.md are design questions, not problem-understanding questions

**The signal is not "features complete." It's "no more surprises."**

When this feels true → move to `phase2-graduate.md`.
