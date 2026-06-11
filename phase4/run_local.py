#!/usr/bin/env python3
"""Local smoke test for Phase 4."""
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

try:
    from agent import agent
except ImportError as exc:
    print("Import error:", exc)
    sys.exit(1)

obs = {
    "player": 0,
    "step": 25,
    "planets": [
        [0, 0, 20.0, 20.0, 2.0, 50, 3],
        [1, -1, 60.0, 60.0, 1.5, 10, 5],
        [2, 1, 80.0, 80.0, 1.8, 30, 2],
    ],
    "fleets": [],
    "angular_velocity": 0.03,
    "initial_planets": [
        [0, 0, 20.0, 20.0, 2.0, 50, 3],
        [1, -1, 60.0, 60.0, 1.5, 10, 5],
    ],
    "comets": [],
    "comet_planet_ids": [],
}

moves = agent(obs)
print(f"Phase 4 smoke test: {len(moves)} moves")
for m in moves:
    assert len(m) == 3
print("OK")
