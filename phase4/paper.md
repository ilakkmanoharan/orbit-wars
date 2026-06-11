# Phase 4 — NFM × ASRA × Atlas-GS for Orbit Wars

## Concept Mapping

This phase applies three research frameworks to the Orbit Wars Kaggle agent:

```text
NFM (Nature Foundation Models)     → State + Action → State' world dynamics
NFM-Worlds / Atlas-GS                → Gaussian spatial value field over the board
ASRA (Adaptive Scientific Reasoning)   → Observe → Hypothesize → Experiment → Act
```

### NFM — World Model Layer

The NFM core abstraction is:

```text
State_t + Action_t → State_{t+1}
```

In Orbit Wars:
- **State** — planet positions, owners, garrisons, production, active fleets, step
- **Action** — fleet launches `[from_planet_id, angle, num_ships]`
- **Dynamics** — production ticks, orbit rotation, fleet movement, combat resolution

`world_model.py` implements explicit state representation and transition via forward simulation.

### Atlas-GS — Spatial Value Field

Atlas-GS learns persistent 3D scene representations via Gaussian Splatting. We adapt this to Orbit Wars as a **2D Gaussian value splat**:

Each planet contributes a kernel centered at `(x, y)` with weight:
- `production` for capturable neutrals
- `production × 0.5` for enemy planets
- `production × 2` for owned planets (defense value)

Target priority = `gaussian_value(target) / (eta + 1)`

This replaces naive nearest-neighbor with spatially-aware economic reasoning.

### ASRA — Scientific Reasoning Loop

ASRA's loop:

```text
Observe → Hypothesize → Experiment → Analyze → Act
```

Each turn the agent:
1. **Observes** the full game state
2. **Hypothesizes** 5 strategic theories (mapped to policy clusters)
3. **Experiments** by forward-simulating each hypothesis 15 turns
4. **Analyzes** predicted ship counts and production totals
5. **Acts** on the opening moves of the best-supported hypothesis

| Hypothesis | Strategic theory | Policy cluster |
|---|---|---|
| H1: Economy | High-production neutrals win long games | `expand_neutrals` + `conservative` |
| H2: Aggression | Eliminate weakest enemy early | `snipe_weakest` + `expand_all` |
| H3: Comets | Temporary captures compound ship count | `comet_rush` |
| H4: Consolidation | Reinforce before expanding | `reinforce_home` |
| H5: Balanced | Mixed expansion across all targets | `expand_all` |

## Why Phase 4?

Ladder results showed Phase 2 (sim picker, μ=600) outperformed Phase 3 (meta-strategy, μ≈385–398). Phase 4 keeps Phase 2's simulation core but adds:

- Gaussian spatial targeting (Atlas-GS)
- Explicit world-state transitions (NFM)
- Hypothesis-driven policy selection (ASRA)

## Files

| File | Role |
|---|---|
| `world_model.py` | NFM state + dynamics; Atlas-GS value field |
| `asra_reasoner.py` | Hypothesis generation, experiment, analysis |
| `geometry.py` | Orbit prediction, intercept, sun check |
| `simulation.py` | Forward rollout engine |
| `agent.py` | ASRA loop + move generation |
| `main.py` | Kaggle entry point |

## Submit

```bash
./scripts/bundle.sh phase4
kaggle competitions submit orbit-wars -f submission.tar.gz -m "phase4 nfm-asra-atlas v1"
```
