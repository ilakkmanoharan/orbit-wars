# Phase 7 — Disciplined A/B on Phase 2

## Problem

Phase 2 scores **μ 600**. Phases 3–6 regressed to 346–427 by adding complexity that misaligned simulation with winning.

## Approach

Fork Phase 2 exactly. Apply **one mechanical fix per variant**. Never change the eval function or add meta-layers.

**Phase 7a:** Target deduplication only — **ladder result μ 423.1 (failed)**.

See `private/phase-analysis.md`. Phase 8 supersedes 7b with comet paths + static boost.

Phase 7a was identical to phase 2 except:
- 6-policy sim picker
- Eval: `prod×10 + ships + owned×5`
- Target scoring: `production / (eta + 1)`
- Sim depth: 12
- **Added:** `claimed_targets` deduplication (hurt score)

## Roadmap

See `private/phase7-plan.md` for variants 7b–7g (comet paths, fleets in sim, replay fixes, tuning).

## Submit

```bash
./scripts/bundle.sh phase7
kaggle competitions submit orbit-wars -f submission.tar.gz -m "phase7a target dedup"
```
