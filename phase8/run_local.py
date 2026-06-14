#!/usr/bin/env python3
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from agent import agent

obs = {
    "player": 0, "step": 45,
    "planets": [[0, 0, 20.0, 20.0, 2.0, 50, 4], [1, -1, 60.0, 60.0, 1.5, 10, 5]],
    "fleets": [], "angular_velocity": 0.03,
    "initial_planets": [[0, 0, 20.0, 20.0, 2.0, 50, 4]],
    "comets": [], "comet_planet_ids": [],
}

t0 = time.perf_counter()
moves = agent(obs)
print(f"Phase 8: {len(moves)} moves in {(time.perf_counter()-t0)*1000:.1f}ms — OK")
