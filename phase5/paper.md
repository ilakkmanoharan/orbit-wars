# Phase 5 — Combat-Aware Long-Horizon Expansion

## Goal

Beat the μ=600 ceiling shared by Phase 2 and Phase 4. Ladder analysis showed Phase 3 meta-strategy hurt (μ≈385), while Phase 2's direct sim picker and Phase 4's NFM/ASRA layer both plateaued at 600.

Phase 5 keeps the proven **6-policy simulation picker** but fixes three concrete weaknesses:

## Improvements over Phase 4

| Fix | Problem | Solution |
|---|---|---|
| **Target deduplication** | Multiple fleets to same planet → tie combat destroys all attackers | One claim per target per turn |
| **Long-horizon scoring** | `production/eta` ignores remaining game length | `production × (500−step) / (eta+1)` |
| **Incoming fleet defense** | Enemy fleets capture undefended high-prod planets | Detect threats; send reinforcements |
| **Fleet size optimization** | Minimum ships move slowly on distant targets | Upsize fleet when speed gain reduces ETA significantly |
| **Deeper rollout** | 12-turn sim misses mid-game consequences | 18-turn simulation depth |

## Architecture

```
phase5/
  allocator.py   — smart move generation (claims, defense, sizing)
  geometry.py    — intercept + threat projection
  simulation.py  — 18-turn rollout, horizon-weighted eval
  agent.py       — 6-policy picker + top-2 move merge
  main.py
```

## Submit

```bash
./scripts/bundle.sh phase5
kaggle competitions submit orbit-wars -f submission.tar.gz -m "phase5 combat-aware v1"
```
