#!/usr/bin/env python3
import os
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from agent import agent

obs = {
    "player": 0,
    "step": 45,
    "planets": [
        [0, 0, 20.0, 20.0, 2.0, 50, 4],
        [1, -1, 60.0, 60.0, 1.5, 10, 5],
        [2, 1, 80.0, 80.0, 1.8, 30, 2],
    ],
    "fleets": [],
    "angular_velocity": 0.03,
    "initial_planets": [
        [0, 0, 20.0, 20.0, 2.0, 50, 4],
        [1, -1, 60.0, 60.0, 1.5, 10, 5],
    ],
    "comets": [],
    "comet_planet_ids": [],
}

t0 = time.perf_counter()
moves = agent(obs)
elapsed = time.perf_counter() - t0
print(f"Phase 6: {len(moves)} moves in {elapsed*1000:.1f}ms — OK")
