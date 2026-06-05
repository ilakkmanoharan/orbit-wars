#!/usr/bin/env python3
"""Local test: Phase 1 vs random and vs Phase 0."""
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PHASE0 = os.path.join(os.path.dirname(ROOT), "phase0", "main.py")
sys.path.insert(0, ROOT)

try:
    from kaggle_environments import make
except ImportError as exc:
    print("Install kaggle-environments>=1.28.0:", exc)
    sys.exit(1)

AGENT = os.path.join(ROOT, "main.py")


def run_match(agents, seed):
    env = make("orbit_wars", configuration={"seed": seed})
    env.run(agents)
    final = env.steps[-1]
    return [s.reward for s in final]


def main():
    print("Phase 1 vs random (seed=42)...")
    rewards = run_match([AGENT, "random"], 42)
    print("  rewards:", rewards)

    print("Phase 1 vs Phase 0 (seed=42)...")
    rewards = run_match([AGENT, PHASE0], 42)
    print("  rewards:", rewards)
    print("Phase 1 local test complete.")


if __name__ == "__main__":
    main()
