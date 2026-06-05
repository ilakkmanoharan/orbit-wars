# Phase 3: Polish & Meta-Strategy

## Objective

Phase 3 is the **competition submission candidate**. It refines Phase 2 with free-for-all (FFA) awareness, endgame conservatism, proactive comet timing, and a second strategic variant for the "latest 2 submissions" rule.

## Key Competition Meta-Rules

| Rule | Phase 3 Response |
|---|---|
| Only latest 2 submissions count for final ranking | Maintain two distinct variants: `main.py` (balanced) and `variant_aggressive.py` |
| Win/loss only — score margin irrelevant | When ahead on ship count, switch to conservative policy |
| 4-player FFA common | Don't all-in attack one enemy while others expand |
| Comets spawn at steps 50/150/250/350/450 | Pre-position fleets during steps 40–49, 140–149, etc. |
| 1 second per turn | Cap simulation depth; cache policy scores within a turn |

## Architecture

```
phase3/
  paper.md
  geometry.py
  simulation.py
  agent.py           ← polished policy picker with game-phase awareness
  variant_aggressive.py  ← alternate submission (expand-all focus)
  main.py
  run_local.py
  benchmark.py       ← batch test vs prior phases
```

## Game-Phase Detection

The agent classifies each turn into one of three phases:

### Opening (steps 0–80)
- Prioritize high-production neutrals.
- Keep home garrison at `max(5, production * 2)`.
- Ignore enemy planets unless extremely weak (≤ 5 ships).

### Midgame (steps 81–350)
- Full policy picker from Phase 2.
- Comet windows: during 10 steps before each comet spawn, boost `comet_rush` weight.
- FFA check: if ≥ 2 enemies have more total ships than us, prefer `expand_neutrals` over `snipe_weakest`.

### Endgame (steps 351–500)
- If our ship count ≥ 1.2× the second-place estimate, use `conservative` only.
- Otherwise continue midgame policies but avoid reinforcing enemies by attacking fortified planets.

## Ship Count Estimation

Each turn, estimate total ships per player:

```
total = sum(planet.ships for owned planets) + sum(fleet.ships for owned fleets)
```

In FFA, attacking the weakest enemy is only preferred when we are not the weakest player overall.

## Comet Pre-Positioning

Comets spawn at steps `[50, 150, 250, 350, 450]`. During steps `spawn - 10` through `spawn - 1`:

1. Parse `obs["comets"]` for incoming path endpoints.
2. Boost comet target scores by 3×.
3. Launch from the nearest owned planet with surplus ≥ 10 ships.

Comets have production 1 but are free captures — valuable for ship count tiebreakers.

## Two Submission Variants

**Balanced (`main.py`)** — default Phase 3 agent with game-phase logic.

**Aggressive (`variant_aggressive.py`)** — always uses `expand_all` + `snipe_weakest` policies, higher risk/reward. Submit as your second tracked bot if the ladder meta favors aggression.

```bash
# Primary
tar -czf phase3.tar.gz -C phase3 main.py geometry.py simulation.py agent.py
kaggle competitions submit orbit-wars -f phase3.tar.gz -m "phase3 balanced final"

# Alternate (second tracked submission)
tar -czf phase3_agg.tar.gz -C phase3 variant_aggressive.py geometry.py simulation.py agent.py
# Rename entry: variant_aggressive.py exports agent() — bundle with main.py name or submit as tarball
```

## Benchmarking

Run `benchmark.py` to compare Phase 3 vs all prior phases over N seeds:

```bash
python phase3/benchmark.py --seeds 20
```

Target: > 60% win rate vs Phase 2, > 90% vs Phase 0.

## Replay Analysis Workflow

When you lose on the ladder:

```bash
kaggle competitions episodes <SUBMISSION_ID> -v
kaggle competitions replay <EPISODE_ID> -p ./replays
kaggle competitions logs <EPISODE_ID> 0 -p ./logs
```

Look for: sun losses, failed comet intercepts, home planet snipes, over-commitment to one front.

## Success Criteria

- Validation episode passes consistently
- Win rate vs Phase 2 > 60% locally
- Average turn time < 300 ms
- Two distinct variants submitted before June 23 deadline
