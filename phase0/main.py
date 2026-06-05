"""Phase 0 — Baseline expander with safety guards. Submit this file to Kaggle."""
import math

try:
    from kaggle_environments.envs.orbit_wars.orbit_wars import Planet, CENTER, SUN_RADIUS
except ImportError:
    from collections import namedtuple

    Planet = namedtuple(
        "Planet", ["id", "owner", "x", "y", "radius", "ships", "production"]
    )
    CENTER = 50.0
    SUN_RADIUS = 10.0

MIN_GARRISON = 5


def _parse_obs(obs):
    if isinstance(obs, dict):
        player = obs.get("player", 0)
        raw_planets = obs.get("planets", [])
    else:
        player = obs.player
        raw_planets = obs.planets
    return player, [Planet(*p) for p in raw_planets]


def _segment_crosses_sun(x0, y0, x1, y1, margin=0.5):
    """True if line segment (x0,y0)->(x1,y1) passes within sun radius."""
    px, py = CENTER, CENTER
    dx, dy = x1 - x0, y1 - y0
    length_sq = dx * dx + dy * dy
    if length_sq == 0.0:
        return math.hypot(x0 - px, y0 - py) < SUN_RADIUS + margin
    t = max(0.0, min(1.0, ((px - x0) * dx + (py - y0) * dy) / length_sq))
    proj_x = x0 + t * dx
    proj_y = y0 + t * dy
    return math.hypot(proj_x - px, proj_y - py) < SUN_RADIUS + margin


def agent(obs):
    moves = []
    player, planets = _parse_obs(obs)
    if not planets:
        return moves

    my_planets = [p for p in planets if p.owner == player and p.ships > MIN_GARRISON]
    targets = [p for p in planets if p.owner != player]
    if not my_planets or not targets:
        return moves

    for mine in my_planets:
        nearest = min(targets, key=lambda t: math.hypot(mine.x - t.x, mine.y - t.y))
        ships_needed = nearest.ships + 1
        available = mine.ships - MIN_GARRISON
        if available < ships_needed:
            continue

        angle = math.atan2(nearest.y - mine.y, nearest.x - mine.x)
        spawn_x = mine.x + math.cos(angle) * (mine.radius + 0.1)
        spawn_y = mine.y + math.sin(angle) * (mine.radius + 0.1)
        if _segment_crosses_sun(spawn_x, spawn_y, nearest.x, nearest.y):
            continue

        moves.append([mine.id, angle, ships_needed])

    return moves
