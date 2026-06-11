#!/usr/bin/env python3
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from agent import agent

obs = {
    "player": 0,
    "step": 100,
    "planets": [
        [0, 0, 20.0, 20.0, 2.0, 50, 4],
        [1, -1, 60.0, 60.0, 1.5, 10, 5],
        [2, 1, 80.0, 80.0, 1.8, 30, 2],
    ],
    "fleets": [[0, 1, 40.0, 40.0, 0.5, 2, 25]],
    "angular_velocity": 0.03,
    "initial_planets": [
        [0, 0, 20.0, 20.0, 2.0, 50, 4],
        [1, -1, 60.0, 60.0, 1.5, 10, 5],
    ],
    "comet_planet_ids": [],
}

moves = agent(obs)
print(f"Phase 5: {len(moves)} moves — OK")
