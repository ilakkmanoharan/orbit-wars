"""Move allocation — phase2 core + P0/P1 fixes (Phase 6)."""
import math

from geometry import (
    launch_angle,
    segment_crosses_sun,
    estimate_eta,
    optimize_fleet_size,
    in_comet_window,
)


def min_garrison(production, mode="normal", is_home=False):
    base = max(5, production) if is_home else max(3, production)
    return base * 2 if mode == "conservative" else base


def ships_needed(target, is_enemy=False):
    needed = target.ships + 1
    if is_enemy:
        needed = int(target.ships * 1.5) + 1
    return needed


def build_moves(planets, player, init, av, comet_pids, comet_groups, policy, step=0):
    my = [p for p in planets if p.owner == player]
    moves = []
    if not my:
        return moves

    reserve_mode = "conservative" if policy == "conservative" else "normal"
    home = max(my, key=lambda p: (p.production, p.ships)) if my else None

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
        home = max(owned, key=lambda p: p.production)
        for src in my:
            if src.id == home.id:
                continue
            reserve = min_garrison(src.production, reserve_mode)
            send = src.ships - reserve
            if send < 3:
                continue
            angle = math.atan2(home.y - src.y, home.x - src.x)
            moves.append([src.id, angle, send])
        return moves

    scored = []
    for src in my:
        is_home_src = home is not None and src.id == home.id
        reserve = min_garrison(src.production, reserve_mode, is_home=is_home_src)
        for tgt in targets:
            is_enemy = tgt.owner >= 0
            min_need = ships_needed(tgt, is_enemy)
            if src.ships - reserve < min_need:
                continue

            max_send = src.ships - reserve
            if tgt.production >= 4 and min_need < max_send:
                ships, eta = optimize_fleet_size(
                    src.x, src.y, tgt.x, tgt.y, tgt.radius,
                    min_need, max_send, tgt.id, init, av, tgt.radius, comet_groups,
                )
            else:
                ships = min_need
                eta = estimate_eta(
                    src.x, src.y, tgt.x, tgt.y, tgt.radius, ships,
                    tgt.id, init, av, tgt.radius, comet_groups,
                )

            if policy == "conservative" and (tgt.owner != -1 or eta > 20):
                continue

            val = tgt.production / (eta + 1)
            if tgt.id in comet_pids:
                val *= 2.0 if in_comet_window(step) else 1.5
            scored.append((val, src, tgt, ships, eta))

    scored.sort(key=lambda x: x[0], reverse=True)
    used = {p.id: 0 for p in my}
    claimed_targets = set()

    for val, src, tgt, ships, eta in scored:
        if tgt.id in claimed_targets:
            continue
        is_home_src = home is not None and src.id == home.id
        reserve = min_garrison(src.production, reserve_mode, is_home=is_home_src)
        if src.ships - reserve - used[src.id] < ships:
            continue

        angle, _ = launch_angle(
            src.x, src.y, tgt.x, tgt.y, tgt.id, init, av, tgt.radius, ships, comet_groups,
        )
        sx = src.x + math.cos(angle) * (src.radius + 0.1)
        sy = src.y + math.sin(angle) * (src.radius + 0.1)
        if segment_crosses_sun(sx, sy, tgt.x, tgt.y):
            continue

        moves.append([src.id, angle, int(ships)])
        used[src.id] += ships
        claimed_targets.add(tgt.id)

    return moves
