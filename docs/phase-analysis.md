# Orbit Wars — Phase Score Analysis

**Best submission:** Phase 2 v1 — **μ 600.0**  
**Target:** μ 1000

Full roadmap: `private/phase8-plan.md` (local)

## Score Summary

| Phase | μ Score | vs Phase 2 |
|---|---|---|
| **2 v1** | **600.0** | baseline |
| 0 baseline | 479.2 | −20% |
| 1 v1 | 477.6 | −20% |
| 6 v2 | 468.3 | −22% |
| 5 combat-aware | 426.1 | −29% |
| 7a target dedup | 423.1 | −29% |
| 3 aggressive | 398.0 | −34% |
| 3 v1 | 390.4 | −35% |
| 4 nfm-asra-atlas | 346.3 | −42% |
| 6 v1 | — | Error |

## Why Phase 2 Wins (μ 600)

- **6-policy sim picker** — expand_neutrals, expand_all, snipe_weakest, reinforce_home, comet_rush, conservative
- **12-turn rollout** with eval `prod×10 + ships + owned×5`
- **Aggressive garrison** `max(3, production)` — ships go out fast
- **No meta layers** — no game-phase switches, ASRA, or policy weights

## Why Each Later Phase Regressed

| Phase | What it added | Why score dropped |
|---|---|---|
| 0 | Nearest-target greedy | No sim, no ETA scoring |
| 1 | Intercept geometry | Greedy without sim validation |
| 3 | Game-phase + FFA filters | Over-constrained policy picker |
| 4 | ASRA/NFM/Atlas layers | Extra indirection, changed eval |
| 5 | Horizon eval, defensive moves, dedup | Misaligned sim, drained expansion |
| 6 | Bundled P0–P2 fixes | Policy weights + dedup + changed sim |
| 7a | Target dedup only | **Fewer ships deployed per turn** |

## Key Lesson

**Target deduplication (7a → 423) proves Phase 2's multi-fleet launches are a feature, not a bug.** Aggressive deployment beats tie-combat waste avoidance.

## Phase 8 Strategy

Literal Phase 2 + **scoring/geometry only** (no dedup, no meta):

1. Comet path ETA via `obs["comets"].paths`
2. Static planet value boost (1.25×)
3. Comet pre-spawn window boost (2.0× within 10 steps of spawn)

See `phase8/paper.md` for implementation details.
