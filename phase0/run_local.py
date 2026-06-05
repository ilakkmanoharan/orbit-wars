#!/usr/bin/env python3
"""Smoke test for Phase 0 agent."""
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

try:
    from kaggle_environments import make
except ImportError as exc:
    print("Install kaggle-environments>=1.28.0:", exc)
    sys.exit(1)

AGENT = os.path.join(ROOT, "main.py")


def main():
    env = make("orbit_wars", configuration={"seed": 42}, debug=True)
    env.run([AGENT, "random"])
    final = env.steps[-1]
    for i, state in enumerate(final):
        print(f"Player {i}: reward={state.reward}, status={state.status}")
    print("Phase 0 smoke test passed.")


if __name__ == "__main__":
    main()
