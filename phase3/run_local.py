#!/usr/bin/env python3
"""Local test: Phase 3 vs Phase 2."""
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PHASE2 = os.path.join(os.path.dirname(ROOT), "phase2", "main.py")
sys.path.insert(0, ROOT)

try:
    from kaggle_environments import make
except ImportError as exc:
    print("Install kaggle-environments>=1.28.0:", exc)
    sys.exit(1)

AGENT = os.path.join(ROOT, "main.py")


def main():
    env = make("orbit_wars", configuration={"seed": 42})
    env.run([AGENT, PHASE2])
    final = env.steps[-1]
    for i, s in enumerate(final):
        print(f"Player {i}: reward={s.reward}")
    print("Phase 3 local test complete.")


if __name__ == "__main__":
    main()
