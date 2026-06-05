# Phase 0: Setup & First Submission

## Objective

Phase 0 establishes the development environment, validates the submission pipeline, and deploys a **minimal working bot** to the Kaggle ladder. The goal is not strength — it is to confirm that your agent runs under competition constraints and begins accumulating skill-rating episodes immediately.

## What This Phase Delivers

| Artifact | Purpose |
|---|---|
| `main.py` | Competition-ready agent (baseline expander) |
| `run_local.py` | Local smoke test against `random` |
| This paper | Documents setup steps and design rationale |

## Setup Checklist

1. **Join the competition** at [kaggle.com/competitions/orbit-wars](https://www.kaggle.com/competitions/orbit-wars) and accept the rules before the entry deadline (June 16, 2026).
2. **Install dependencies:**
   ```bash
   pip install "kaggle-environments>=1.28.0" kaggle
   ```
3. **Configure Kaggle CLI** — save your API token to `~/.kaggle/access_token` or run `kaggle auth login`.
4. **Run local smoke test:**
   ```bash
   python phase0/run_local.py
   ```
5. **Submit to the ladder:**
   ```bash
   kaggle competitions submit orbit-wars -f phase0/main.py -m "phase0 baseline v1"
   ```

## Agent Design: Baseline Expander

The Phase 0 bot implements the competition starter pattern with three safety guards:

### 1. Nearest-target expansion

For each owned planet with surplus ships, find the nearest planet not owned by the player and launch enough ships to capture it (`target.ships + 1`).

### 2. Garrison floor

Never drain a planet below **5 ships**. This prevents home-planet snipes and avoids sending fleets so small they move at minimum speed (1 unit/turn).

### 3. Sun avoidance

Before launching, check whether the straight-line path from the planet edge to the target crosses the sun (center at `(50, 50)`, radius 10). Fleets crossing the sun are destroyed — skipping these launches prevents silent ship loss.

## Why Submit Early?

The evaluation system gives newly submitted bots **more frequent episodes** for faster rating feedback. A weak but valid bot on the ladder is more valuable than a perfect bot submitted on the last day with no rating history.

## Limitations (Intentional)

Phase 0 does **not** predict orbiting planet positions, prioritize production value, or plan ahead. It will lose to any bot that does. Phases 1–3 address these gaps progressively.

## Success Criteria

- [ ] Local test completes without errors
- [ ] Kaggle validation episode passes (self-play)
- [ ] Submission appears on the Submissions page with status other than Error
- [ ] Average turn time well under 1 second
