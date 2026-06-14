# Phase 8 — Phase 2 + Better Targeting

See `private/phase-analysis.md` for full score post-mortem across all phases.

## Problem

Phase 2 scores **μ 600**. Phase 7a (target dedup only) scored **423** — reducing fleet deployment hurts more than tie-combat waste.

## Phase 8 changes (scoring/geometry only)

1. **Comet path intercept** — ETA via `obs["comets"].paths`, not orbit math
2. **Static planet boost** — 1.25× value for non-orbiting high-prod neutrals
3. **Comet pre-spawn window** — 2.0× comet value in 10 steps before spawn (50/150/250/350/450)

## Unchanged from Phase 2

- 6-policy sim picker, depth 12, eval `prod×10 + ships + owned×5`
- No target dedup, no policy weights, no meta layers

## Submit

```bash
./scripts/bundle.sh phase8
kaggle competitions submit orbit-wars -f submission.tar.gz -m "phase8 comet paths + static boost"
```
