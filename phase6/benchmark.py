#!/usr/bin/env python3
"""Benchmark phase6 vs phase2 (requires orbit_wars env)."""
import argparse
import os
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(ROOT)
sys.path.insert(0, ROOT)

try:
    from kaggle_environments import make
except ImportError:
    print("SKIP: kaggle-environments not installed")
    sys.exit(0)

PHASE6 = os.path.join(ROOT, "main.py")
PHASE2 = os.path.join(BASE, "phase2", "main.py")


def win_rate(agent_a, agent_b, seeds):
    wins = ties = 0
    for seed in seeds:
        env = make("orbit_wars", configuration={"seed": seed})
        env.run([agent_a, agent_b])
        final = env.steps[-1]
        if final[0].reward > final[1].reward:
            wins += 1
        elif final[0].reward == final[1].reward:
            ties += 1
    return wins, ties, len(seeds)


def profile_turns(n=20):
    from agent import agent as a6
    obs = {
        "player": 0, "step": 100,
        "planets": [[0, 0, 20.0, 20.0, 2.0, 50, 4], [1, -1, 60.0, 60.0, 1.5, 10, 5]],
        "fleets": [], "angular_velocity": 0.03,
        "initial_planets": [[0, 0, 20.0, 20.0, 2.0, 50, 4]],
        "comets": [], "comet_planet_ids": [],
    }
    t0 = time.perf_counter()
    for _ in range(n):
        a6(obs)
    avg = (time.perf_counter() - t0) / n
    print(f"Avg turn time: {avg*1000:.1f}ms ({n} iterations)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=int, default=20)
    parser.add_argument("--profile", action="store_true")
    args = parser.parse_args()

    if args.profile:
        profile_turns()
        return

    try:
        make("orbit_wars", configuration={"seed": 0})
    except Exception as exc:
        print("SKIP: orbit_wars unavailable:", exc)
        sys.exit(0)

    seeds = list(range(args.seeds))
    wins, ties, total = win_rate(PHASE6, PHASE2, seeds)
    print(f"Phase 6 vs Phase 2: {wins}/{total} wins, {ties} ties ({wins/total:.0%})")


if __name__ == "__main__":
    main()
