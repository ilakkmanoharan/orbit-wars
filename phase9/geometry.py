"""Geometry (Phase 9) — phase2 + guarded comet path intercept."""
import math

try:
    from kaggle_environments.envs.orbit_wars.orbit_wars import (
        CENTER,
        ROTATION_RADIUS_LIMIT,
        SUN_RADIUS,
    )
except ImportError:
    CENTER = 50.0
    ROTATION_RADIUS_LIMIT = 50.0
    SUN_RADIUS = 10.0

MAX_FLEET_SPEED = 6.0


def fleet_speed(ships, max_speed=MAX_FLEET_SPEED):
    if ships <= 1:
        return 1.0
    ratio = math.log(max(ships, 1)) / math.log(1000)
    return min(1.0 + (max_speed - 1.0) * ratio ** 1.5, max_speed)


def initial_by_id(initial_planets):
    return {p[0]: p for p in initial_planets}


def _field(obj, key, default=None):
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def comet_group_for(planet_id, comet_groups):
    for group in comet_groups or []:
        if planet_id in _field(group, "planet_ids", []):
            return group
    return None


def comet_on_board(planet_id, comet_groups):
    group = comet_group_for(planet_id, comet_groups)
    if group is None:
        return False
    return _field(group, "path_index", -1) >= 0


def comet_index_in_group(planet_id, group):
    for i, pid in enumerate(_field(group, "planet_ids", [])):
        if pid == planet_id:
            return i
    return -1


def comet_position_at(planet_id, comet_groups, steps_ahead, fallback_x, fallback_y):
    group = comet_group_for(planet_id, comet_groups)
    if group is None or _field(group, "path_index", -1) < 0:
        return fallback_x, fallback_y
    idx = comet_index_in_group(planet_id, group)
    if idx < 0:
        return fallback_x, fallback_y
    paths = _field(group, "paths", [])
    if idx >= len(paths):
        return fallback_x, fallback_y
    path = paths[idx]
    pi = _field(group, "path_index", 0) + steps_ahead
    if pi < 0 or pi >= len(path):
        return fallback_x, fallback_y
    return path[pi][0], path[pi][1]


def predict_position(planet_id, initial_planets, angular_velocity, steps_ahead,
                     current_x, current_y, radius, comet_groups=None):
    if comet_groups and comet_on_board(planet_id, comet_groups):
        return comet_position_at(planet_id, comet_groups, steps_ahead, current_x, current_y)

    init = initial_planets.get(planet_id)
    if init is None:
        return current_x, current_y
    ix, iy = init[2], init[3]
    r = math.hypot(ix - CENTER, iy - CENTER)
    if r + radius >= ROTATION_RADIUS_LIMIT:
        return current_x, current_y
    angle0 = math.atan2(iy - CENTER, ix - CENTER)
    angle = angle0 + angular_velocity * steps_ahead
    return CENTER + r * math.cos(angle), CENTER + r * math.sin(angle)


def segment_crosses_sun(x0, y0, x1, y1, margin=0.5):
    px, py = CENTER, CENTER
    dx, dy = x1 - x0, y1 - y0
    length_sq = dx * dx + dy * dy
    if length_sq == 0.0:
        return math.hypot(x0 - px, y0 - py) < SUN_RADIUS + margin
    t = max(0.0, min(1.0, ((px - x0) * dx + (py - y0) * dy) / length_sq))
    return math.hypot(x0 + t * dx - px, y0 + t * dy - py) < SUN_RADIUS + margin


def estimate_eta(sx, sy, tx, ty, tr, ships, pid, init_map, av, radius,
                 comet_groups=None, max_steps=200):
    fx, fy = sx, sy
    for step in range(1, max_steps + 1):
        px, py = predict_position(pid, init_map, av, step, tx, ty, radius, comet_groups)
        angle = math.atan2(py - fy, px - fx)
        sp = fleet_speed(ships)
        fx += math.cos(angle) * sp
        fy += math.sin(angle) * sp
        if math.hypot(fx - px, fy - py) <= tr:
            return step
    return max_steps


def launch_angle(sx, sy, tx, ty, pid, init_map, av, radius, ships, comet_groups=None):
    eta = estimate_eta(sx, sy, tx, ty, radius, ships, pid, init_map, av, radius, comet_groups)
    px, py = predict_position(pid, init_map, av, eta, tx, ty, radius, comet_groups)
    return math.atan2(py - sy, px - sx), eta
