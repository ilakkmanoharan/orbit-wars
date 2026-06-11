"""Combat-aware move allocation (Phase 5)."""
import math

from geometry import (
    MAX_STEPS,
    launch_angle,
    segment_crosses_sun,
    estimate_eta,
    in_comet_window,
    fleet_hits_planet,
    optimize_fleet_size,
)


def min_garrison(production, policy):
    base = max(3, production)
    return base * 2 if policy == "conservative" else base


def ships_needed(target, is_enemy=False):
    needed = target.ships + 1
    if is_enemy:
        needed = int(target.ships * 1.5) + 1
    return needed


def long_horizon_value(production, step, eta, comet=False):
    remaining = max(1, MAX_STEPS - step)
    val = production * remaining / (eta + 1.0)
    if comet:
        val *= 1.8
    return val


def defensive_moves(planets, fleets, player, init_map, av):
    """Reinforce planets threatened by incoming enemy fleets."""
    moves = []
    my = [p for p in planets if p.owner == player]
    if not my:
        return moves

    threatened = {}
    for f in fleets:
        if f[1] == player:
            continue
        eta, hit = fleet_hits_planet(f[2], f[3], f[4], f[6], planets, init_map, av, owner_filter=player)
        if hit is None or eta is None:
            continue
        pid = hit.id if hasattr(hit, "id") else hit[0]
        hit_ships = hit.ships if hasattr(hit, "ships") else hit[5]
        if f[6] > hit_ships * 0.4:
            threatened[pid] = max(threatened.get(pid, 0), f[6])

    for pid, threat in threatened.items():
        planet = next(p for p in my if p.id == pid)
        need = max(3, int(threat - planet.ships) + 2)
        if need <= 0:
            continue
        donors = [p for p in my if p.id != pid and p.ships > min_garrison(p.production, "normal") + need]
        if not donors:
            continue
        src = min(donors, key=lambda p: math.hypot(p.x - planet.x, p.y - planet.y))
        reserve = min_garrison(src.production, "normal")
        send = min(need, src.ships - reserve)
        if send < 2:
            continue
        angle = math.atan2(planet.y - src.y, planet.x - src.x)
        moves.append([src.id, angle, send])

    return moves


def build_moves(planets, player, init_map, av, comet_pids, policy, step, fleets=None):
    my = [p for p in planets if p.owner == player]
    moves = []
    if not my:
        return moves

    if fleets:
        moves.extend(defensive_moves(planets, fleets, player, init_map, av))

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
        if policy == "comet_rush" and t.id not in comet_pids:
            continue
        targets.append(t)

    if policy == "snipe_weakest" and targets:
        targets = [min(targets, key=lambda t: t.ships)]

    if policy == "reinforce_home":
        owned = [p for p in my if p.production >= 2]
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
            is_enemy = tgt.owner >= 0
            min_need = ships_needed(tgt, is_enemy)
            if src.ships - reserve < min_need:
                continue
            max_send = src.ships - reserve
            ships, eta = optimize_fleet_size(
                src.x, src.y, tgt.x, tgt.y, tgt.radius,
                min_need, max_send, tgt.id, init_map, av, tgt.radius,
            )
            if policy == "conservative" and (tgt.owner != -1 or eta > 22):
                continue
            val = long_horizon_value(tgt.production, step, eta, tgt.id in comet_pids)
            if tgt.id in comet_pids and in_comet_window(step):
                val *= 1.5
            scored.append((val, src, tgt, ships, eta))

    scored.sort(key=lambda x: x[0], reverse=True)
    used_ships = {p.id: 0 for p in my}
    claimed_targets = set()

    for val, src, tgt, ships, eta in scored:
        if tgt.id in claimed_targets:
            continue
        reserve = min_garrison(src.production, policy)
        if src.ships - reserve - used_ships[src.id] < ships:
            continue
        angle, _ = launch_angle(src.x, src.y, tgt.x, tgt.y, tgt.id, init_map, av, tgt.radius, ships)
        sx = src.x + math.cos(angle) * (src.radius + 0.1)
        sy = src.y + math.sin(angle) * (src.radius + 0.1)
        if segment_crosses_sun(sx, sy, tgt.x, tgt.y):
            continue
        moves.append([src.id, angle, ships])
        used_ships[src.id] += ships
        claimed_targets.add(tgt.id)

    return moves
