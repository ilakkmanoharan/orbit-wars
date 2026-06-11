# Phase 6 — Combat-Aware Long-Horizon Expansion (Phase 2 Foundation)

## Goal

Beat μ=600 (Phase 2) and target μ=1000 by fixing mechanical bugs — not adding theory layers.

## What changed from Phase 2

| Fix | Description |
|---|---|
| Target deduplication | One fleet per target per turn (multi-attacker tie rule) |
| Fleets in simulator | Existing in-flight fleets included in rollout |
| Comet path intercept | Uses `comets.paths` for position prediction |
| Sun in simulator | Fleets crossing sun destroyed during sim |
| Multi-step rollout | Greedy `expand_neutrals` follow-up after turn 1 |
| Better opponent model | Enemies attack weak owned planets when no neutrals |
| Fleet size optimization | Larger fleets for distant high-prod targets |
| FFA policy weighting | Boost neutral farming when 2+ stronger enemies |
| Home garrison | Higher floor on home planet (`max(5, prod)`) |

## What we kept from Phase 2

- Direct 6-policy sim picker (no ASRA hypothesis layer)
- Value function: `prod×10 + ships + owned×5`
- `production / (eta + 1)` target scoring

## Submit

```bash
./scripts/bundle.sh phase6
kaggle competitions submit orbit-wars -f submission.tar.gz -m "phase6 v1"
```
