"""Geometry helpers (Phase 2 — same as Phase 1)."""
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


def predict_position(planet_id, initial_planets, angular_velocity, steps_ahead, current_x, current_y, radius):
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


def estimate_eta(sx, sy, tx, ty, tr, ships, pid, init_map, av, radius, max_steps=200):
    fx, fy = sx, sy
    for step in range(1, max_steps + 1):
        px, py = predict_position(pid, init_map, av, step, tx, ty, radius)
        angle = math.atan2(py - fy, px - fx)
        sp = fleet_speed(ships)
        fx += math.cos(angle) * sp
        fy += math.sin(angle) * sp
        if math.hypot(fx - px, fy - py) <= tr:
            return step
    return max_steps


def launch_angle(sx, sy, tx, ty, pid, init_map, av, radius, ships):
    eta = estimate_eta(sx, sy, tx, ty, radius, ships, pid, init_map, av, radius)
    px, py = predict_position(pid, init_map, av, eta, tx, ty, radius)
    return math.atan2(py - sy, px - sx), eta
