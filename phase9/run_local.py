#!/usr/bin/env python3
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from agent import agent

obs = {
    "player": 0, "step": 55,
    "planets": [[0, 0, 20.0, 20.0, 2.0, 50, 4], [1, -1, 60.0, 60.0, 1.5, 10, 5]],
    "fleets": [], "angular_velocity": 0.03,
    "initial_planets": [[0, 0, 20.0, 20.0, 2.0, 50, 4]],
    "comets": [], "comet_planet_ids": [],
}
t0 = time.perf_counter()
print(f"Phase 9: {len(agent(obs))} moves in {(time.perf_counter()-t0)*1000:.1f}ms — OK")
