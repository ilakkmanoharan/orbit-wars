"""Phase 3 polished agent with game-phase and FFA awareness."""
import math

try:
    from kaggle_environments.envs.orbit_wars.orbit_wars import Planet, Fleet
except ImportError:
    from collections import namedtuple

    Planet = namedtuple(
        "Planet", ["id", "owner", "x", "y", "radius", "ships", "production"]
    )
    Fleet = namedtuple(
        "Fleet", ["id", "owner", "x", "y", "angle", "from_planet_id", "ships"]
    )

from geometry import initial_by_id, launch_angle, segment_crosses_sun, estimate_eta, in_comet_window
from simulation import state_from_obs, simulate, player_totals

SIM_DEPTH = 12
OPENING_END = 80
ENDGAME_START = 351


def _parse_obs(obs):
    if isinstance(obs, dict):
        player = obs.get("player", 0)
        planets = [Planet(*p) for p in obs.get("planets", [])]
        fleets = [Fleet(*f) for f in obs.get("fleets", [])]
        av = obs.get("angular_velocity", 0.025)
        init = initial_by_id(obs.get("initial_planets", []))
        comet_pids = set(obs.get("comet_planet_ids", []))
        step = obs.get("step", 0)
    else:
        player = obs.player
        planets = [Planet(*p) for p in obs.planets]
        fleets = [Fleet(*f) for f in getattr(obs, "fleets", [])]
        av = getattr(obs, "angular_velocity", 0.025)
        init = initial_by_id(getattr(obs, "initial_planets", []))
        comet_pids = set(getattr(obs, "comet_planet_ids", []))
        step = getattr(obs, "step", 0)
    return player, planets, fleets, av, init, comet_pids, step


def game_phase(step):
    if step <= OPENING_END:
        return "opening"
    if step >= ENDGAME_START:
        return "endgame"
    return "midgame"


def min_garrison(production, phase, policy):
    base = max(3, production)
    if phase == "opening":
        return max(5, production * 2)
    if policy == "conservative" or phase == "endgame":
        return base * 2
    return base


def _build_moves(planets, player, init, av, comet_pids, policy, phase, comet_boost=False):
    my = [p for p in planets if p.owner == player]
    moves = []
    if not my:
        return moves

    targets = []
    for t in planets:
        if t.owner == player:
            continue
        is_neutral = t.owner == -1
        is_enemy = t.owner >= 0
        if policy == "expand_neutrals" and not is_neutral:
            continue
        if policy == "expand_all" and phase == "opening" and is_enemy and t.ships > 5:
            continue
        if policy == "snipe_weakest" and not is_enemy:
            continue
        if policy == "comet_rush" and t.id not in comet_pids:
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
            reserve = min_garrison(src.production, phase, policy)
            send = src.ships - reserve
            if send < 3:
                continue
            angle = math.atan2(home.y - src.y, home.x - src.x)
            moves.append([src.id, angle, send])
        return moves

    scored = []
    for src in my:
        reserve = min_garrison(src.production, phase, policy)
        for tgt in targets:
            needed = tgt.ships + 1
            if tgt.owner >= 0:
                needed = int(tgt.ships * 1.5) + 1
            if src.ships - reserve < needed:
                continue
            eta = estimate_eta(src.x, src.y, tgt.x, tgt.y, tgt.radius, needed,
                               tgt.id, init, av, tgt.radius)
            if policy == "conservative" and eta > 25:
                continue
            val = tgt.production / (eta + 1)
            if tgt.id in comet_pids:
                val *= 3.0 if comet_boost else 1.5
            scored.append((val, src, tgt, needed))

    scored.sort(key=lambda x: x[0], reverse=True)
    used = {p.id: 0 for p in my}
    for val, src, tgt, needed in scored:
        reserve = min_garrison(src.production, phase, policy)
        if src.ships - reserve - used[src.id] < needed:
            continue
        angle, _ = launch_angle(src.x, src.y, tgt.x, tgt.y, tgt.id, init, av, tgt.radius, needed)
        sx = src.x + math.cos(angle) * (src.radius + 0.1)
        sy = src.y + math.sin(angle) * (src.radius + 0.1)
        if segment_crosses_sun(sx, sy, tgt.x, tgt.y):
            continue
        moves.append([src.id, angle, needed])
        used[src.id] += needed

    return moves


ALL_POLICIES = [
    "expand_neutrals",
    "expand_all",
    "snipe_weakest",
    "reinforce_home",
    "comet_rush",
    "conservative",
]


def policies_for_context(phase, totals, player, step, aggressive=False):
    if aggressive:
        return ["expand_all", "snipe_weakest", "comet_rush"]

    if phase == "opening":
        return ["expand_neutrals", "comet_rush", "conservative"]

    if phase == "endgame":
        sorted_players = sorted(totals.items(), key=lambda x: x[1], reverse=True)
        if sorted_players and sorted_players[0][0] == player:
            second = sorted_players[1][1] if len(sorted_players) > 1 else 0
            if totals.get(player, 0) >= second * 1.2:
                return ["conservative", "reinforce_home"]
        return ["expand_all", "snipe_weakest", "conservative"]

    # midgame FFA
    my_total = totals.get(player, 0)
    stronger_enemies = sum(1 for pid, t in totals.items() if pid != player and t > my_total)
    if stronger_enemies >= 2:
        return ["expand_neutrals", "comet_rush", "conservative", "reinforce_home"]
    return ALL_POLICIES


def decide(obs, aggressive=False):
    player, planets, fleets, av, init, comet_pids, step = _parse_obs(obs)
    phase = game_phase(step)
    sim_planets, sim_fleets, _, init_map, _ = state_from_obs(obs, player)
    totals = player_totals(sim_planets, sim_fleets)

    comet_boost = in_comet_window(step)
    policies = policies_for_context(phase, totals, player, step, aggressive)

    best_moves = []
    best_score = float("-inf")

    for policy in policies:
        moves = _build_moves(planets, player, init, av, comet_pids, policy, phase, comet_boost)
        score = simulate(sim_planets, sim_fleets, player, init_map, av, moves, SIM_DEPTH)
        if score > best_score:
            best_score = score
            best_moves = moves

    return best_moves


def agent(obs):
    return decide(obs, aggressive=False)
