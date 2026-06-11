"""Phase 6 — phase2 sim picker + P0/P1/P2 improvements."""
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

SIM_DEPTH = 12

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
            obs.get("comets", []),
            obs.get("step", 0),
        )
    return (
        obs.player,
        [Planet(*p) for p in obs.planets],
        getattr(obs, "fleets", []),
        getattr(obs, "angular_velocity", 0.025),
        initial_by_id(getattr(obs, "initial_planets", [])),
        set(getattr(obs, "comet_planet_ids", [])),
        getattr(obs, "comets", []),
        getattr(obs, "step", 0),
    )


def _player_totals(planets, fleets_raw, player):
    totals = {}
    for p in planets:
        if p.owner >= 0:
            totals[p.owner] = totals.get(p.owner, 0) + p.ships
    for f in fleets_raw:
        owner = f[1] if isinstance(f, (list, tuple)) else f.owner
        ships = f[6] if isinstance(f, (list, tuple)) else f.ships
        if owner >= 0:
            totals[owner] = totals.get(owner, 0) + ships
    return totals


def _policy_weights(planets, fleets_raw, player):
    totals = _player_totals(planets, fleets_raw, player)
    my_total = totals.get(player, 0)
    stronger = sum(1 for pid, t in totals.items() if pid != player and t > my_total)
    owned = sum(1 for p in planets if p.owner == player)

    weights = {p: 1.0 for p in POLICIES}
    if stronger >= 2:
        weights["expand_neutrals"] *= 1.3
        weights["conservative"] *= 1.2
        weights["snipe_weakest"] *= 0.5
    if totals and my_total <= min(totals.values()):
        weights["expand_all"] *= 1.2
        weights["comet_rush"] *= 1.2
    if owned < 3:
        weights["expand_neutrals"] *= 1.15
    return weights


def decide(obs):
    player, planets, fleets_raw, av, init, comet_pids, comet_groups, step = _parse_obs(obs)
    if not planets:
        return []

    sim_planets, sim_fleets, _, init_map, _, cg, cp, sim_step = state_from_obs(obs, player)
    weights = _policy_weights(planets, fleets_raw, player)

    best_moves = []
    best_score = float("-inf")

    for policy in POLICIES:
        moves = build_moves(planets, player, init, av, comet_pids, comet_groups, policy, step)
        score = simulate(
            sim_planets, sim_fleets, player, init_map, av, moves, SIM_DEPTH,
            comet_groups=cg, comet_pids=cp, step=sim_step,
        )
        score *= weights[policy]
        if score > best_score:
            best_score = score
            best_moves = moves

    return best_moves


def agent(obs):
    return decide(obs)
