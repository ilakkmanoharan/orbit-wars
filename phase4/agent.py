"""Phase 4 agent — NFM world model + Atlas-GS targeting + ASRA reasoning."""
import math

try:
    from kaggle_environments.envs.orbit_wars.orbit_wars import Planet
except ImportError:
    from collections import namedtuple

    Planet = namedtuple(
        "Planet", ["id", "owner", "x", "y", "radius", "ships", "production"]
    )

from geometry import initial_by_id, launch_angle, segment_crosses_sun, estimate_eta, in_comet_window
from world_model import parse_world, target_score
from simulation import state_from_obs
from asra_reasoner import reason


def min_garrison(production, policy):
    base = max(3, production)
    return base * 2 if policy == "conservative" else base


def _build_moves(planets, world, policy):
    """Generate moves for a policy using Atlas-GS target scoring."""
    player = world.player
    my = [p for p in planets if p.owner == player]
    moves = []
    if not my:
        return moves

    targets = []
    for t in planets:
        if t.owner == player:
            continue
        is_neutral = t.owner == -1
        is_enemy = t.owner >= 0 and t.owner != player
        if policy == "expand_neutrals" and not is_neutral:
            continue
        if policy == "snipe_weakest" and not is_enemy:
            continue
        if policy == "comet_rush" and t.id not in world.comet_pids:
            continue
        targets.append(t)

    if policy == "snipe_weakest" and targets:
        targets = [min(targets, key=lambda t: t.ships)]

    if policy == "reinforce_home":
        owned = [p for p in my if p.production >= 1]
        if not owned:
            return moves
        home = max(owned, key=lambda p: (p.production, p.ships))
        for src in my:
            if src.id == home.id:
                continue
            reserve = min_garrison(src.production, policy)
            send = src.ships - reserve
            if send < 3:
                continue
            angle = math.atan2(home.y - src.y, home.x - src.x)
            moves.append([src.id, angle, send])
        return moves

    scored = []
    for src in my:
        reserve = min_garrison(src.production, policy)
        for tgt in targets:
            needed = tgt.ships + 1
            if tgt.owner >= 0:
                needed = int(tgt.ships * 1.5) + 1
            if src.ships - reserve < needed:
                continue
            eta = estimate_eta(
                src.x, src.y, tgt.x, tgt.y, tgt.radius, needed,
                tgt.id, world.init_map, world.angular_velocity, tgt.radius,
            )
            if policy == "conservative" and (tgt.owner != -1 or eta > 22):
                continue
            val = target_score(world, src, tgt, eta)
            if tgt.id in world.comet_pids and in_comet_window(world.step):
                val *= 2.0
            scored.append((val, src, tgt, needed))

    scored.sort(key=lambda x: x[0], reverse=True)
    used = {p.id: 0 for p in my}
    for val, src, tgt, needed in scored:
        reserve = min_garrison(src.production, policy)
        if src.ships - reserve - used[src.id] < needed:
            continue
        angle, _ = launch_angle(
            src.x, src.y, tgt.x, tgt.y, tgt.id,
            world.init_map, world.angular_velocity, tgt.radius, needed,
        )
        sx = src.x + math.cos(angle) * (src.radius + 0.1)
        sy = src.y + math.sin(angle) * (src.radius + 0.1)
        if segment_crosses_sun(sx, sy, tgt.x, tgt.y):
            continue
        moves.append([src.id, angle, needed])
        used[src.id] += needed

    return moves


def decide(obs):
    world = parse_world(obs)
    planets = [Planet(*p) for p in world.planets]
    if not planets:
        return []

    sim_ctx = state_from_obs(obs, world.player)
    return reason(_build_moves, world, planets, sim_ctx)


def agent(obs):
    return decide(obs)
