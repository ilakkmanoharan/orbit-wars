# Phase 1: Strong Heuristic Bot

## Objective

Phase 1 replaces naive nearest-neighbor expansion with a **production-aware, geometry-informed heuristic**. The bot should consistently beat random agents and weak baselines without any forward simulation or machine learning.

## Core Improvements Over Phase 0

| Feature | Phase 0 | Phase 1 |
|---|---|---|
| Target selection | Nearest planet | Highest `production / (eta + 1)` score |
| Garrison policy | Fixed 5 ships | `max(3, production)` per planet |
| Moving targets | Aims at current position | Predicts orbit position at fleet arrival |
| Sun avoidance | Yes | Yes (shared geometry module) |
| Comets | Ignored | Basic intercept when comets are active |

## Architecture

```
phase1/
  paper.md       ← this document
  geometry.py    ← orbit prediction, fleet speed, ETA, sun check
  agent.py       ← heuristic decision loop
  main.py        ← Kaggle entry point
  run_local.py   ← local test runner
```

## Geometry Module (`geometry.py`)

### Fleet speed

Fleet speed follows the competition formula:

```
speed = 1.0 + (maxSpeed - 1.0) * (log(ships) / log(1000))^1.5
```

Larger fleets arrive faster but leave the source planet more exposed. Phase 1 sends the **minimum ships needed to capture** rather than half the garrison.

### Orbit prediction

Inner planets (where `orbital_radius + planet_radius < 50`) rotate around the sun at `angular_velocity` radians per turn. Given a planet's entry in `initial_planets`, we compute:

```
current_angle = initial_angle + angular_velocity * step_delta
position = (CENTER + r*cos(angle), CENTER + r*sin(angle))
```

### ETA estimation

To intercept a moving planet, we iterate turn-by-turn:

1. Advance fleet position by `fleet_speed(ships)` along the launch angle.
2. Advance target planet position by one rotation step.
3. Stop when distance ≤ planet radius (collision).

The launch angle is recomputed each iteration toward the predicted target position (pursuit guidance).

### Sun segment check

Before committing a launch, we verify the path from spawn point to target does not pass within `SUN_RADIUS` of `(50, 50)`.

## Heuristic Agent (`agent.py`)

Each turn the agent:

1. Parses planets, fleets, comets, and player ID from the observation.
2. Computes a **minimum garrison** for each owned planet: `max(3, production)`.
3. Scores every attackable target:
   - **Neutrals**: `production / (eta + 1)` — high production close by wins.
   - **Enemy planets**: same formula, but only if we have ≥ 1.5× required ships (avoid costly trades).
4. Greedy assignment: best `(source, target)` pairs are executed until planets run out of surplus ships.
5. **Comet bonus**: if active comets exist, boost score for nearby comets we can reach within 30 turns.

## Design Rationale

- **Production is king**: A production-5 planet generates 5 ships/turn. Capturing it early compounds over 500 turns.
- **Minimum capture force**: Sending `garrison + 1` ships minimizes exposure while guaranteeing capture against neutrals.
- **No over-commitment on enemies**: Attacking only with overwhelming force avoids pyrrhic victories in multi-fleet combat.

## Submission

```bash
tar -czf phase1.tar.gz -C phase1 main.py geometry.py agent.py
kaggle competitions submit orbit-wars -f phase1.tar.gz -m "phase1 heuristic v1"
```

Or submit `main.py` alone if you inline imports (not recommended — use tarball).

## Success Criteria

- Win rate vs `random` approaches 100% over 20+ seeds
- Win rate vs Phase 0 bot > 60%
- No timeouts; average turn < 50 ms

## Known Limitations

- Greedy assignment can send multiple fleets to the same target in one turn (wasted in multi-attacker combat).
- No lookahead — a patient opponent can out-expand on the far side of the map.
- Phase 2 addresses this with simulation.
