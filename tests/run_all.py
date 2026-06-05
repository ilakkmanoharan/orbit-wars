#!/usr/bin/env python3
"""Run smoke tests for all phases when orbit_wars is available."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    from kaggle_environments import make
except ImportError:
    print("SKIP: kaggle-environments not installed")
    sys.exit(0)

try:
    make("orbit_wars", configuration={"seed": 0})
except Exception as exc:
    print("SKIP: orbit_wars not available (need kaggle-environments>=1.28.0):", exc)
    sys.exit(0)

PHASES = ["phase0", "phase1", "phase2", "phase3"]


def test_phase(name):
    agent_path = os.path.join(ROOT, name, "main.py")
    env = make("orbit_wars", configuration={"seed": 42})
    env.run([agent_path, "random"])
    final = env.steps[-1]
    assert all(s.status == "DONE" or s.status is None for s in final), name
    print(f"  {name}: OK (rewards={[s.reward for s in final]})")


def main():
    print("Running phase smoke tests...")
    for name in PHASES:
        test_phase(name)
    print("All phases passed.")


if __name__ == "__main__":
    main()
