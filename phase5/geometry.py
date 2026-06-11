"""Geometry helpers (Phase 5)."""
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
COMET_SPAWN_STEPS = [50, 150, 250, 350, 450]
MAX_STEPS = 500


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


def in_comet_window(step, window=10):
    return any(0 <= spawn - step <= window for spawn in COMET_SPAWN_STEPS)


def _pid(p):
    return p.id if hasattr(p, "id") else p[0]


def _powner(p):
    return p.owner if hasattr(p, "owner") else p[1]


def _px(p):
    return p.x if hasattr(p, "x") else p[2]


def _py(p):
    return p.y if hasattr(p, "y") else p[3]


def _pradius(p):
    return p.radius if hasattr(p, "radius") else p[4]


def fleet_hits_planet(fx, fy, angle, ships, planets, init_map, av, owner_filter=None, max_steps=80):
    """Project fleet path; return (eta, planet) on first collision."""
    x, y = fx, fy
    for step in range(1, max_steps + 1):
        sp = fleet_speed(ships)
        x += math.cos(angle) * sp
        y += math.sin(angle) * sp
        if not (0 <= x <= 100 and 0 <= y <= 100):
            return None, None
        for p in planets:
            px, py = predict_position(_pid(p), init_map, av, step, _px(p), _py(p), _pradius(p))
            if math.hypot(x - px, y - py) <= _pradius(p):
                if owner_filter is None or _powner(p) == owner_filter:
                    return step, p
                break
    return None, None


def optimize_fleet_size(sx, sy, tx, ty, tr, min_ships, max_ships, pid, init_map, av, radius):
    """Pick fleet size that minimizes ETA within [min_ships, max_ships]."""
    best_ships = min_ships
    best_eta = estimate_eta(sx, sy, tx, ty, tr, min_ships, pid, init_map, av, radius)
    for ships in range(min_ships + 1, max_ships + 1, max(1, (max_ships - min_ships) // 4)):
        eta = estimate_eta(sx, sy, tx, ty, tr, ships, pid, init_map, av, radius)
        if eta < best_eta:
            best_eta = eta
            best_ships = ships
    return best_ships, best_eta
