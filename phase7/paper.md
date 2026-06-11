# Phase 7 — Disciplined A/B on Phase 2

## Problem

Phase 2 scores **μ 600**. Phases 3–6 regressed to 346–427 by adding complexity that misaligned simulation with winning.

## Approach

Fork Phase 2 exactly. Apply **one mechanical fix per variant**. Never change the eval function or add meta-layers.

## Phase 7a (current): Target Deduplication

Combat tie rule: equal attackers → all ships destroyed. Phase 2 may launch multiple fleets at the same target in one turn, wasting ships.

**Single change:** track `claimed_targets` in move builder; at most one fleet per target per turn.

Everything else identical to phase 2:
- 6-policy sim picker
- Eval: `prod×10 + ships + owned×5`
- Target scoring: `production / (eta + 1)`
- Sim depth: 12

## Roadmap

See `private/phase7-plan.md` for variants 7b–7g (comet paths, fleets in sim, replay fixes, tuning).

## Submit

```bash
./scripts/bundle.sh phase7
kaggle competitions submit orbit-wars -f submission.tar.gz -m "phase7a target dedup"
```
