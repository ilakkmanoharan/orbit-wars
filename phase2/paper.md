# Phase 2: Simulation & Search

## Objective

Phase 2 adds **forward simulation** to choose among candidate move sets each turn. Instead of committing to a single greedy heuristic, the bot evaluates several strategies by rolling the game state forward 10–15 turns and picking the opening moves that maximize a hand-crafted value function.

## Why Simulation?

Heuristic bots are reactive — they make locally optimal decisions without considering how the board evolves. Common failure modes:

- Sending a fleet that arrives after an enemy reinforcement
- Over-expanding toward one quadrant while neutrals in another go uncontested
- Draining home planet garrison before a counter-attack lands

Lightweight simulation catches these by projecting consequences before acting.

## Architecture

```
phase2/
  paper.md
  geometry.py      ← shared with Phase 1 (orbit, ETA, sun)
  simulation.py    ← simplified forward model + value function
  agent.py         ← policy picker: generate candidates → simulate → pick best
  main.py
  run_local.py
```

## Simulation Model (`simulation.py`)

The simulator is intentionally **simplified** — it does not replicate every game rule exactly, but captures enough dynamics for relative comparison between candidate policies.

### State representation

A `SimState` holds:
- Planet list (id, owner, x, y, radius, ships, production)
- Active fleets (owner, x, y, angle, ships)
- Current step counter

### Simplified turn advance

Each simulated turn:

1. **Production** — owned planets generate ships.
2. **Apply our moves** — launch fleets from specified move list.
3. **Opponent model** — each enemy/neutral planet with surplus sends half its garrison toward the nearest neutral (crude but sufficient for comparison).
4. **Fleet movement** — move all fleets one step; resolve planet collisions with simplified combat (`attacker_ships - garrison`, capture if positive).
5. **Planet rotation** — update orbiting planet positions.

### Value function

```
score = sum(production for owned planets) * 10
      + sum(ships on owned planets)
      + sum(ships in owned fleets)
      + 5 * count(owned planets)
```

Production is weighted heavily because it represents future ship income over the remaining game.

## Policy Picker (`agent.py`)

Each turn, generate **candidate move sets** from distinct strategies:

| Policy | Behavior |
|---|---|
| `expand_neutrals` | Phase 1 heuristic restricted to neutral targets only |
| `expand_all` | Phase 1 heuristic on all targets |
| `snipe_weakest` | Attack the enemy planet with lowest garrison |
| `reinforce_home` | Send surplus from outer planets toward highest-production owned planet |
| `comet_rush` | Prioritize capturable comets |
| `conservative` | Only expand to neutrals within ETA ≤ 20, keep 2× garrison floor |

For each candidate:
1. Clone current state.
2. Apply candidate moves for turn 0.
3. Simulate 12 turns with the opponent model handling enemy/neutral reactions.
4. Record the value function score.

Execute the **first turn's moves** from the highest-scoring candidate.

## Performance Budget

With 6 candidates × 12 turns × ~40 planets, simulation stays under ~100 ms on typical hardware — well within the 1-second turn limit. If needed, reduce `SIM_DEPTH` or candidate count.

## Submission

```bash
tar -czf phase2.tar.gz -C phase2 main.py geometry.py simulation.py agent.py
kaggle competitions submit orbit-wars -f phase2.tar.gz -m "phase2 sim-picker v1"
```

## Success Criteria

- Win rate vs Phase 1 bot > 55% over 20 seeds
- Average turn time < 200 ms
- No validation errors on Kaggle

## Known Limitations

- Opponent model is crude — real opponents may behave very differently.
- Simplified combat ignores multi-attacker resolution and sun collisions during simulation.
- Phase 3 refines opponent modeling for FFA and adds endgame conservatism.
