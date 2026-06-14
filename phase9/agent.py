"""Phase 9 — Phase 2 scoring + guarded comet path intercept only."""
import math

try:
    from kaggle_environments.envs.orbit_wars.orbit_wars import Planet
except ImportError:
    from collections import namedtuple

    Planet = namedtuple(
        "Planet", ["id", "owner", "x", "y", "radius", "ships", "production"]
    )

from geometry import (
    initial_by_id,
    launch_angle,
    segment_crosses_sun,
    estimate_eta,
    comet_on_board,
)
from simulation import state_from_obs, simulate

SIM_DEPTH = 13

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
            obs.get("angular_velocity", 0.025),
            initial_by_id(obs.get("initial_planets", [])),
            set(obs.get("comet_planet_ids", [])),
            obs.get("comets", []),
        )
    return (
        obs.player,
        [Planet(*p) for p in obs.planets],
        getattr(obs, "angular_velocity", 0.025),
        initial_by_id(getattr(obs, "initial_planets", [])),
        set(getattr(obs, "comet_planet_ids", [])),
        getattr(obs, "comets", []),
    )


def min_garrison(production, mode="normal"):
    base = max(3, production)
    return base * 2 if mode == "conservative" else base


def _comet_groups_for(target_id, comet_groups):
    if comet_on_board(target_id, comet_groups):
        return comet_groups
    return None


def _skip_comet_target(tgt, comet_pids, comet_groups):
    if tgt.id not in comet_pids:
        return False
    if tgt.x < 0 or tgt.y < 0:
        return not comet_on_board(tgt.id, comet_groups)
    return False


def _build_moves(planets, player, init, av, comet_pids, comet_groups, policy):
    my = [p for p in planets if p.owner == player]
    moves = []
    if not my:
        return moves

    reserve_mode = "conservative" if policy == "conservative" else "normal"
    targets = []
    for t in planets:
        if t.owner == player:
            continue
        if _skip_comet_target(t, comet_pids, comet_groups):
            continue
        is_neutral = t.owner == -1
        is_enemy = t.owner >= 0 and t.owner != player
        if policy == "expand_neutrals" and not is_neutral:
            continue
        if policy == "snipe_weakest" and not is_enemy:
            continue
        if policy == "comet_rush" and t.id not in comet_pids:
            continue
        targets.append(t)

    if policy == "snipe_weakest" and targets:
        targets = [min(targets, key=lambda t: t.ships)]

    if policy == "reinforce_home":
        owned = [p for p in my if p.production >= 2]
        if not owned:
            return moves
        home = max(owned, key=lambda p: p.production)
        for src in my:
            if src.id == home.id:
                continue
            reserve = min_garrison(src.production, reserve_mode)
            send = src.ships - reserve
            if send < 3:
                continue
            angle = math.atan2(home.y - src.y, home.x - src.x)
            moves.append([src.id, angle, send])
        return moves

    scored = []
    for src in my:
        reserve = min_garrison(src.production, reserve_mode)
        for tgt in targets:
            needed = tgt.ships + 1
            if tgt.owner >= 0:
                needed = int(tgt.ships * 1.5) + 1
            if src.ships - reserve < needed:
                continue
            cg = _comet_groups_for(tgt.id, comet_groups)
            eta = estimate_eta(
                src.x, src.y, tgt.x, tgt.y, tgt.radius, needed,
                tgt.id, init, av, tgt.radius, cg,
            )
            if policy == "conservative" and (tgt.owner != -1 or eta > 20):
                continue
            val = tgt.production / (eta + 1)
            if tgt.id in comet_pids:
                val *= 1.5
            scored.append((val, src, tgt, needed, eta, cg))

    scored.sort(key=lambda x: x[0], reverse=True)
    used = {p.id: 0 for p in my}
    for val, src, tgt, needed, eta, cg in scored:
        reserve = min_garrison(src.production, reserve_mode)
        if src.ships - reserve - used[src.id] < needed:
            continue
        angle, _ = launch_angle(
            src.x, src.y, tgt.x, tgt.y, tgt.id, init, av, tgt.radius, needed, cg,
        )
        sx = src.x + math.cos(angle) * (src.radius + 0.1)
        sy = src.y + math.sin(angle) * (src.radius + 0.1)
        if segment_crosses_sun(sx, sy, tgt.x, tgt.y):
            continue
        moves.append([src.id, angle, needed])
        used[src.id] += needed

    return moves


def decide(obs):
    player, planets, av, init, comet_pids, comet_groups = _parse_obs(obs)
    sim_planets, sim_fleets, _, init_map, _ = state_from_obs(obs, player)

    best_moves = []
    best_score = float("-inf")

    for policy in POLICIES:
        moves = _build_moves(planets, player, init, av, comet_pids, comet_groups, policy)
        score = simulate(sim_planets, sim_fleets, player, init_map, av, moves, SIM_DEPTH)
        if score > best_score:
            best_score = score
            best_moves = moves

    return best_moves


def agent(obs):
    return decide(obs)
