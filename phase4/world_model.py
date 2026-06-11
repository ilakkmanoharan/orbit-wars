"""NFM world model + Atlas-GS Gaussian value field for Orbit Wars."""
import math

from geometry import CENTER


class WorldState:
    """NFM State_t — explicit representation of the game world."""

    __slots__ = ("step", "player", "planets", "fleets", "angular_velocity", "init_map", "comet_pids")

    def __init__(self, step, player, planets, fleets, angular_velocity, init_map, comet_pids):
        self.step = step
        self.player = player
        self.planets = planets
        self.fleets = fleets
        self.angular_velocity = angular_velocity
        self.init_map = init_map
        self.comet_pids = comet_pids


def parse_world(obs, player=None):
    if isinstance(obs, dict):
        p = player if player is not None else obs.get("player", 0)
        planets = obs.get("planets", [])
        fleets = obs.get("fleets", [])
        av = obs.get("angular_velocity", 0.025)
        init = {x[0]: x for x in obs.get("initial_planets", [])}
        comets = set(obs.get("comet_planet_ids", []))
        step = obs.get("step", 0)
    else:
        p = player if player is not None else obs.player
        planets = obs.planets
        fleets = getattr(obs, "fleets", [])
        av = getattr(obs, "angular_velocity", 0.025)
        init = {x[0]: x for x in getattr(obs, "initial_planets", [])}
        comets = set(getattr(obs, "comet_planet_ids", []))
        step = getattr(obs, "step", 0)
    return WorldState(step, p, planets, fleets, av, init, comets)


def gaussian_kernel(dx, dy, sigma):
    return math.exp(-(dx * dx + dy * dy) / (2.0 * sigma * sigma))


def planet_weight(planet, player, comet_pids):
    """Atlas-GS splat weight for a planet."""
    pid, owner, x, y, radius, ships, production = planet[:7]
    sigma = max(radius * 2.5, 2.0)
    if owner == player:
        return production * 2.0, sigma
    if owner == -1:
        boost = 2.0 if pid in comet_pids else 1.0
        return production * boost, sigma
    return production * 0.6, sigma


def value_at(world, x, y, for_player=None):
    """Atlas-GS: sum of Gaussian contributions at point (x, y)."""
    player = for_player if for_player is not None else world.player
    total = 0.0
    for p in world.planets:
        w, sigma = planet_weight(p, player, world.comet_pids)
        if w <= 0:
            continue
        total += w * gaussian_kernel(x - p[2], y - p[3], sigma)
    return total


def target_score(world, source, target, eta, player=None):
    """NFM-informed target value: Gaussian field + production / eta."""
    player = player if player is not None else world.player
    pid, owner, tx, ty, tr, ships, production = target[:7]
    gx = value_at(world, tx, ty, player)
    base = production / (eta + 1.0)
    if pid in world.comet_pids:
        base *= 1.8
    if owner >= 0 and owner != player:
        base *= 0.75
    return base + gx * 0.1


def total_ships(world, player=None):
    player = player if player is not None else world.player
    total = sum(p[5] for p in world.planets if p[1] == player)
    total += sum(f[6] for f in world.fleets if f[1] == player)
    return total


def total_production(world, player=None):
    player = player if player is not None else world.player
    return sum(p[6] for p in world.planets if p[1] == player)
