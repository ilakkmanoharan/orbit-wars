"""Geometry helpers for Orbit Wars agents."""
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
BOARD_SIZE = 100.0


def fleet_speed(ships, max_speed=MAX_FLEET_SPEED):
    if ships <= 1:
        return 1.0
    ratio = math.log(max(ships, 1)) / math.log(1000)
    return min(1.0 + (max_speed - 1.0) * ratio ** 1.5, max_speed)


def orbital_radius(x, y):
    return math.hypot(x - CENTER, y - CENTER)


def is_orbiting(x, y, radius):
    return orbital_radius(x, y) + radius < ROTATION_RADIUS_LIMIT


def initial_by_id(initial_planets):
    return {p[0]: p for p in initial_planets}


def predict_position(planet_id, initial_planets, angular_velocity, steps_ahead, current_x, current_y, radius):
    """Return (x, y) after steps_ahead turns. Uses initial_planets for orbit; static otherwise."""
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
    proj_x = x0 + t * dx
    proj_y = y0 + t * dy
    return math.hypot(proj_x - px, proj_y - py) < SUN_RADIUS + margin


def estimate_eta(source_x, source_y, target_x, target_y, target_radius, ships,
                 planet_id, initial_planets, angular_velocity, radius, max_steps=200):
    """Turns until fleet intercepts target. Uses pursuit toward predicted position."""
    fx, fy = source_x, source_y
    for step in range(1, max_steps + 1):
        tx, ty = predict_position(
            planet_id, initial_planets, angular_velocity, step,
            target_x, target_y, radius,
        )
        angle = math.atan2(ty - fy, tx - fx)
        speed = fleet_speed(ships)
        fx += math.cos(angle) * speed
        fy += math.sin(angle) * speed
        if math.hypot(fx - tx, fy - ty) <= target_radius:
            return step
    return max_steps


def launch_angle(source_x, source_y, target_x, target_y, planet_id, initial_planets,
                 angular_velocity, radius, ships):
    """Angle for intercept at estimated arrival time."""
    eta = estimate_eta(
        source_x, source_y, target_x, target_y, target_radius=radius, ships=ships,
        planet_id=planet_id, initial_planets=initial_planets,
        angular_velocity=angular_velocity, radius=radius,
    )
    tx, ty = predict_position(
        planet_id, initial_planets, angular_velocity, eta,
        target_x, target_y, radius,
    )
    return math.atan2(ty - source_y, tx - source_x), eta


def comet_position(comet_group, planet_index):
    """Current (x, y) of a comet from observation group data."""
    idx = comet_group.get("path_index", 0)
    paths = comet_group.get("paths", [])
    if planet_index >= len(paths):
        return None
    path = paths[planet_index]
    if idx >= len(path):
        return None
    return path[idx][0], path[idx][1]
