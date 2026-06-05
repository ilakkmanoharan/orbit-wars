#!/usr/bin/env python3
"""Batch benchmark Phase 3 against prior phases."""
import argparse
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(ROOT)
sys.path.insert(0, ROOT)

try:
    from kaggle_environments import make
except ImportError as exc:
    print("Install kaggle-environments>=1.28.0:", exc)
    sys.exit(1)

PHASES = {
    "phase0": os.path.join(BASE, "phase0", "main.py"),
    "phase1": os.path.join(BASE, "phase1", "main.py"),
    "phase2": os.path.join(BASE, "phase2", "main.py"),
    "phase3": os.path.join(ROOT, "main.py"),
}


def win_rate(agent_a, agent_b, seeds):
    wins = 0
    for seed in seeds:
        env = make("orbit_wars", configuration={"seed": seed})
        env.run([agent_a, agent_b])
        final = env.steps[-1]
        if final[0].reward > final[1].reward:
            wins += 1
        elif final[0].reward == final[1].reward:
            wins += 0.5
    return wins / len(seeds)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=int, default=10)
    args = parser.parse_args()
    seeds = list(range(args.seeds))

    p3 = PHASES["phase3"]
    for name in ("phase0", "phase1", "phase2"):
        wr = win_rate(p3, PHASES[name], seeds)
        print(f"Phase 3 vs {name}: {wr:.0%} win rate ({args.seeds} seeds)")


if __name__ == "__main__":
    main()
