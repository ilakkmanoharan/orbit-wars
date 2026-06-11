"""Phase 5 — combat-aware long-horizon sim picker."""
import math

try:
    from kaggle_environments.envs.orbit_wars.orbit_wars import Planet
except ImportError:
    from collections import namedtuple

    Planet = namedtuple(
        "Planet", ["id", "owner", "x", "y", "radius", "ships", "production"]
    )

from geometry import initial_by_id
from simulation import state_from_obs, simulate
from allocator import build_moves

SIM_DEPTH = 18

POLICIES = [
    "expand_neutrals",
    "expand_all",
    "snipe_weakest",
    "reinforce_home",
    "comet_rush",
    "conservative",
]


def _parse_obs(obs):
    if isinstance(obs, dict):
        return (
            obs.get("player", 0),
            [Planet(*p) for p in obs.get("planets", [])],
            obs.get("fleets", []),
            obs.get("angular_velocity", 0.025),
            initial_by_id(obs.get("initial_planets", [])),
            set(obs.get("comet_planet_ids", [])),
            obs.get("step", 0),
        )
    return (
        obs.player,
        [Planet(*p) for p in obs.planets],
        getattr(obs, "fleets", []),
        getattr(obs, "angular_velocity", 0.025),
        initial_by_id(getattr(obs, "initial_planets", [])),
        set(getattr(obs, "comet_planet_ids", [])),
        getattr(obs, "step", 0),
    )


def _merge_moves(primary, secondary):
    """Combine non-conflicting moves from top-2 policies."""
    if not secondary:
        return primary
    used_sources = {}
    claimed_targets = set()
    merged = []
    for move in primary:
        merged.append(move)
        used_sources[move[0]] = used_sources.get(move[0], 0) + move[2]
    for move in secondary:
        if move[0] in used_sources:
            continue
        merged.append(move)
    return merged


def decide(obs):
    player, planets, fleets_raw, av, init, comet_pids, step = _parse_obs(obs)
    if not planets:
        return []

    sim_planets, sim_fleets, _, init_map, _, sim_step = state_from_obs(obs, player)

    results = []
    for policy in POLICIES:
        moves = build_moves(planets, player, init, av, comet_pids, policy, step, fleets_raw)
        score = simulate(sim_planets, sim_fleets, player, init_map, av, moves, SIM_DEPTH, sim_step)
        results.append((score, moves, policy))

    results.sort(key=lambda x: x[0], reverse=True)
    best = results[0][1]
    if len(results) > 1 and results[0][0] - results[1][0] < 15:
        return _merge_moves(results[0][1], results[1][1])
    return best


def agent(obs):
    return decide(obs)
