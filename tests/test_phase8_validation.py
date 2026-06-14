#!/usr/bin/env python3
"""Run phase8 agent against orbit_wars interpreter."""
import importlib.util
import os
import sys
import time
from types import SimpleNamespace

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENDOR = os.path.join(ROOT, "tests", "vendor", "orbit_wars", "orbit_wars.py")
PHASE8 = os.path.join(ROOT, "phase8")
sys.path.insert(0, PHASE8)

spec = importlib.util.spec_from_file_location("orbit_wars_env", VENDOR)
ow = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ow)
from agent import agent  # noqa: E402


def obs_to_dict(obs, player):
    return {
        "player": player, "step": getattr(obs, "step", 0),
        "planets": obs.planets, "fleets": obs.fleets,
        "angular_velocity": obs.angular_velocity,
        "initial_planets": obs.initial_planets,
        "comets": obs.comets, "comet_planet_ids": obs.comet_planet_ids,
    }


config = SimpleNamespace(episodeSteps=500, shipSpeed=6.0, cometSpeed=4.0, seed=42)
env = SimpleNamespace(configuration=config, info={}, done=False)
state = [SimpleNamespace(observation=SimpleNamespace(), action=[], reward=0, status="ACTIVE") for _ in range(4)]
times, errors = [], []

for _ in range(500):
    ow.interpreter(state, env)
    if all(s.status == "DONE" for s in state):
        break
    for i, s in enumerate(state):
        if s.status != "ACTIVE":
            continue
        obs = obs_to_dict(s.observation, i)
        t0 = time.perf_counter()
        try:
            s.action = agent(obs)
        except Exception as exc:
            errors.append(exc)
            s.action = []
        times.append(time.perf_counter() - t0)

mx = max(times) if times else 0
print(f"Phase 8 validation: turns={len(times)} max={mx*1000:.1f}ms errors={len(errors)}")
