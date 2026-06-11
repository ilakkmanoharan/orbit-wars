"""Forward simulator — phase2 eval + P0/P1 fidelity (Phase 6)."""
import copy
import math

from geometry import fleet_speed, predict_position, segment_crosses_sun


class SimPlanet:
    __slots__ = ("id", "owner", "x", "y", "radius", "ships", "production")

    def __init__(self, id, owner, x, y, radius, ships, production):
        self.id = id
        self.owner = owner
        self.x = x
        self.y = y
        self.radius = radius
        self.ships = ships
        self.production = production

    def copy(self):
        return SimPlanet(self.id, self.owner, self.x, self.y, self.radius, self.ships, self.production)


class SimFleet:
    __slots__ = ("owner", "x", "y", "angle", "ships")

    def __init__(self, owner, x, y, angle, ships):
        self.owner = owner
        self.x = x
        self.y = y
        self.angle = angle
        self.ships = ships


def state_from_obs(obs, player):
    if isinstance(obs, dict):
        raw = obs.get("planets", [])
        av = obs.get("angular_velocity", 0.025)
        init = {p[0]: p for p in obs.get("initial_planets", [])}
        fleets_raw = obs.get("fleets", [])
        comet_groups = obs.get("comets", [])
        comet_pids = set(obs.get("comet_planet_ids", []))
        step = obs.get("step", 0)
    else:
        raw = obs.planets
        av = getattr(obs, "angular_velocity", 0.025)
        init = {p[0]: p for p in getattr(obs, "initial_planets", [])}
        fleets_raw = getattr(obs, "fleets", [])
        comet_groups = getattr(obs, "comets", [])
        comet_pids = set(getattr(obs, "comet_planet_ids", []))
        step = getattr(obs, "step", 0)

    planets = [SimPlanet(p[0], p[1], p[2], p[3], p[4], p[5], p[6]) for p in raw]
    fleets = [SimFleet(f[1], f[2], f[3], f[4], f[6]) for f in fleets_raw]
    return planets, fleets, av, init, player, comet_groups, comet_pids, step


def evaluate(planets, fleets, player):
    """Phase 2 value function — unchanged."""
    prod = sum(p.production for p in planets if p.owner == player)
    ships = sum(p.ships for p in planets if p.owner == player)
    ships += sum(f.ships for f in fleets if f.owner == player)
    owned = sum(1 for p in planets if p.owner == player)
    return prod * 10 + ships + owned * 5


def _resolve_combat(planet, attacker_owner, attacker_ships):
    if attacker_owner == planet.owner:
        planet.ships += attacker_ships
        return
    if attacker_ships > planet.ships:
        planet.owner = attacker_owner
        planet.ships = attacker_ships - planet.ships
    else:
        planet.ships -= attacker_ships


def _move_fleets(planets, fleets, init_map, av, step, comet_groups=None):
    surviving = []
    for f in fleets:
        ox, oy = f.x, f.y
        speed = fleet_speed(f.ships)
        f.x += math.cos(f.angle) * speed
        f.y += math.sin(f.angle) * speed
        if segment_crosses_sun(ox, oy, f.x, f.y):
            continue
        if not (0 <= f.x <= 100 and 0 <= f.y <= 100):
            continue
        hit = False
        for p in planets:
            px, py = predict_position(p.id, init_map, av, step, p.x, p.y, p.radius, comet_groups)
            if math.hypot(f.x - px, f.y - py) <= p.radius:
                _resolve_combat(p, f.owner, f.ships)
                hit = True
                break
        if not hit:
            surviving.append(f)
    return surviving


def _opponent_moves(planets, player, init_map, av):
    moves = []
    neutrals = [p for p in planets if p.owner == -1]
    my_planets = [p for p in planets if p.owner == player]

    for p in planets:
        if p.owner == player or p.owner == -1:
            continue
        if p.ships < 4:
            continue

        if neutrals:
            nearest = min(neutrals, key=lambda n: math.hypot(p.x - n.x, p.y - n.y))
            send = p.ships // 2
            if send >= 2:
                angle = math.atan2(nearest.y - p.y, nearest.x - p.x)
                moves.append((p.id, angle, send, p.owner))

        if my_planets and p.ships >= 8:
            weak = min(my_planets, key=lambda m: m.ships)
            if p.ships >= int(weak.ships * 1.5) + 1:
                send = max(2, p.ships // 3)
                angle = math.atan2(weak.y - p.y, weak.x - p.x)
                moves.append((p.id, angle, send, p.owner))

    return moves


def apply_launches(planets, fleets, moves, default_owner):
    by_id = {p.id: p for p in planets}
    for move in moves:
        if len(move) == 3:
            pid, angle, num = move
            launch_owner = default_owner
        else:
            pid, angle, num, launch_owner = move
        p = by_id.get(pid)
        if p is None or p.owner != launch_owner or p.ships < num:
            continue
        p.ships -= num
        sx = p.x + math.cos(angle) * (p.radius + 0.1)
        sy = p.y + math.sin(angle) * (p.radius + 0.1)
        fleets.append(SimFleet(launch_owner, sx, sy, angle, num))


def _greedy_followup(planets, player):
    """Lightweight expand-neutrals follow-up (no allocator import)."""
    my = [p for p in planets if p.owner == player]
    neutrals = [p for p in planets if p.owner == -1]
    if not my or not neutrals:
        return []
    moves = []
    used = {p.id: 0 for p in my}
    for src in my:
        reserve = max(3, src.production)
        best = min(neutrals, key=lambda n: math.hypot(src.x - n.x, src.y - n.y))
        needed = best.ships + 1
        if src.ships - reserve - used[src.id] < needed:
            continue
        angle = math.atan2(best.y - src.y, best.x - src.x)
        moves.append([src.id, angle, needed])
        used[src.id] += needed
    return moves


def simulate(planets, fleets, player, init_map, av, our_moves, depth=12,
             comet_groups=None, comet_pids=None, step=0):
    planets = [p.copy() for p in planets]
    fleets = copy.deepcopy(fleets)
    comet_groups = comet_groups or []
    comet_pids = comet_pids or set()
    cur_step = step

    for turn in range(depth):
        cur_step += 1
        for p in planets:
            if p.owner >= 0:
                p.ships += p.production

        if turn == 0:
            turn_moves = our_moves
        else:
            turn_moves = _greedy_followup(planets, player)

        apply_launches(planets, fleets, turn_moves, player)
        opp = _opponent_moves(planets, player, init_map, av)
        apply_launches(planets, fleets, opp, None)

        for p in planets:
            p.x, p.y = predict_position(p.id, init_map, av, 1, p.x, p.y, p.radius, comet_groups)

        fleets = _move_fleets(planets, fleets, init_map, av, cur_step, comet_groups)

    return evaluate(planets, fleets, player)
