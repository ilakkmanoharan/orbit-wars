#!/usr/bin/env python3
import importlib.util, os, sys, time
from types import SimpleNamespace

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "phase9"))
spec = importlib.util.spec_from_file_location("ow", os.path.join(ROOT, "tests/vendor/orbit_wars/orbit_wars.py"))
ow = importlib.util.module_from_spec(spec); spec.loader.exec_module(ow)
from agent import agent

config = SimpleNamespace(episodeSteps=500, shipSpeed=6.0, cometSpeed=4.0, seed=42)
env = SimpleNamespace(configuration=config, info={}, done=False)
state = [SimpleNamespace(observation=SimpleNamespace(), action=[], reward=0, status="ACTIVE") for _ in range(4)]
times, errors = [], []

for _ in range(500):
    ow.interpreter(state, env)
    if all(s.status == "DONE" for s in state): break
    for i, s in enumerate(state):
        if s.status != "ACTIVE": continue
        obs = {"player": i, "step": getattr(s.observation, "step", 0), "planets": s.observation.planets,
               "fleets": s.observation.fleets, "angular_velocity": s.observation.angular_velocity,
               "initial_planets": s.observation.initial_planets, "comets": s.observation.comets,
               "comet_planet_ids": s.observation.comet_planet_ids}
        t0 = time.perf_counter()
        try: s.action = agent(obs)
        except Exception as e: errors.append(e); s.action = []
        times.append(time.perf_counter() - t0)

print(f"Phase 9 validation: turns={len(times)} max={max(times)*1000:.1f}ms errors={len(errors)}")
