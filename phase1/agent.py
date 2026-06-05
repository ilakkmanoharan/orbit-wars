"""Phase 1 heuristic agent."""
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
    comet_position,
)


def _parse_obs(obs):
    if isinstance(obs, dict):
        return (
            obs.get("player", 0),
            [Planet(*p) for p in obs.get("planets", [])],
            obs.get("angular_velocity", 0.025),
            initial_by_id(obs.get("initial_planets", [])),
            obs.get("comets", []),
            obs.get("comet_planet_ids", []),
        )
    return (
        obs.player,
        [Planet(*p) for p in obs.planets],
        getattr(obs, "angular_velocity", 0.025),
        initial_by_id(getattr(obs, "initial_planets", [])),
        getattr(obs, "comets", []),
        getattr(obs, "comet_planet_ids", []),
    )


def min_garrison(production):
    return max(3, production)


def ships_to_capture(target_ships, is_enemy=False):
    needed = target_ships + 1
    if is_enemy:
        needed = int(target_ships * 1.5) + 1
    return needed


def score_target(source, target, initial_map, angular_velocity, is_enemy=False):
    needed = ships_to_capture(target.ships, is_enemy)
    if source.ships - min_garrison(source.production) < needed:
        return None

    eta = estimate_eta(
        source.x, source.y, target.x, target.y, target.radius, needed,
        target.id, initial_map, angular_velocity, target.radius,
    )
    value = target.production / (eta + 1.0)
    if is_enemy:
        value *= 0.8
    return value, needed, eta


def decide(obs):
    player, planets, angular_velocity, initial_map, comets, comet_pids = _parse_obs(obs)
    moves = []
    if not planets:
        return moves

    comet_set = set(comet_pids)
    my_planets = [p for p in planets if p.owner == player]
    if not my_planets:
        return moves

    # Build comet planet lookup from observation
    comet_targets = []
    for group in comets:
        for i, pid in enumerate(group.get("planet_ids", [])):
            pos = comet_position(group, i)
            if pos is None:
                continue
            planet = next((p for p in planets if p.id == pid), None)
            if planet and planet.owner != player:
                comet_targets.append((planet, pos[0], pos[1]))

    candidates = []
    for source in my_planets:
        reserve = min_garrison(source.production)
        if source.ships <= reserve:
            continue

        for target in planets:
            if target.owner == player:
                continue
            is_enemy = target.owner >= 0
            scored = score_target(source, target, initial_map, angular_velocity, is_enemy)
            if scored is None:
                continue
            value, needed, eta = scored
            if target.id in comet_set and eta <= 30:
                value *= 1.5
            candidates.append((value, source.id, target, needed, eta))

    candidates.sort(key=lambda c: c[0], reverse=True)
    used_ships = {p.id: 0 for p in my_planets}

    for value, source_id, target, needed, eta in candidates:
        source = next(p for p in my_planets if p.id == source_id)
        reserve = min_garrison(source.production)
        remaining = source.ships - reserve - used_ships[source_id]
        if remaining < needed:
            continue

        angle, _ = launch_angle(
            source.x, source.y, target.x, target.y, target.id,
            initial_map, angular_velocity, target.radius, needed,
        )
        spawn_x = source.x + math.cos(angle) * (source.radius + 0.1)
        spawn_y = source.y + math.sin(angle) * (source.radius + 0.1)
        if segment_crosses_sun(spawn_x, spawn_y, target.x, target.y):
            continue

        moves.append([source_id, angle, needed])
        used_ships[source_id] += needed

    return moves


def agent(obs):
    return decide(obs)
