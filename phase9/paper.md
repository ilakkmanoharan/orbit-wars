# Phase 9 — Phase 2 + Guarded Comet Paths

## Phase 8 result: μ 559.2 (−41 vs phase 2)

Static boost and 2.0× pre-spawn comet scoring pulled the sim picker toward comets/static targets during opening neutral expansion.

## Phase 9 changes

1. **Guarded comet path ETA** — use `comets.paths` only when `path_index >= 0`
2. **Skip off-board comets** — no launches at (−99,−99)
3. **Phase 2 scoring restored** — `prod/(eta+1)`, comet 1.5× only
4. **SIM_DEPTH 13** — slightly deeper rollout

## Target

Beat phase 2 (μ 600), step toward μ 700–800 via replay-driven phases 10+.

## Submit

```bash
./scripts/bundle.sh phase9
kaggle competitions submit orbit-wars -f submission.tar.gz -m "phase9 guarded comet paths"
```
