#!/usr/bin/env python3
"""Run phase6 agent against orbit_wars interpreter (local validation)."""
import importlib.util
import os
import sys
import time
from types import SimpleNamespace

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENDOR = os.path.join(ROOT, "tests", "vendor", "orbit_wars", "orbit_wars.py")
PHASE6 = os.path.join(ROOT, "phase6")

sys.path.insert(0, PHASE6)

spec = importlib.util.spec_from_file_location("orbit_wars_env", VENDOR)
ow = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ow)

from agent import agent  # noqa: E402


def obs_to_dict(obs):
    if isinstance(obs, dict):
        return obs
    return {
        "player": obs.player,
        "step": getattr(obs, "step", 0),
        "planets": obs.planets,
        "fleets": obs.fleets,
        "angular_velocity": obs.angular_velocity,
        "initial_planets": obs.initial_planets,
        "comets": obs.comets,
        "comet_planet_ids": obs.comet_planet_ids,
        "next_fleet_id": getattr(obs, "next_fleet_id", 0),
        "remainingOverageTime": getattr(obs, "remainingOverageTime", 60),
    }


def run_episode(seed=42, max_steps=500):
    config = SimpleNamespace(episodeSteps=max_steps, shipSpeed=6.0, cometSpeed=4.0, seed=seed)
    env = SimpleNamespace(configuration=config, info={}, done=False)
    state = [
        SimpleNamespace(observation=SimpleNamespace(), action=[], reward=0, status="ACTIVE")
        for _ in range(4)
    ]
    times = []
    errors = []

    for _ in range(max_steps):
        ow.interpreter(state, env)
        if all(s.status == "DONE" for s in state):
            break
        for i, s in enumerate(state):
            if s.status != "ACTIVE":
                continue
            obs = obs_to_dict(s.observation)
            obs["player"] = i
            t0 = time.perf_counter()
            try:
                s.action = agent(obs)
            except Exception as exc:
                errors.append((obs.get("step"), i, exc))
                s.action = []
            elapsed = time.perf_counter() - t0
            times.append(elapsed)
            if elapsed > 1.0:
                errors.append((obs.get("step"), i, f"TIMEOUT {elapsed:.2f}s"))

    return times, errors


if __name__ == "__main__":
    for seed in [0, 1, 42, 99, 12345]:
        times, errors = run_episode(seed=seed)
        avg = sum(times) / len(times) if times else 0
        mx = max(times) if times else 0
        print(f"seed={seed}: turns={len(times)} avg={avg*1000:.1f}ms max={mx*1000:.1f}ms errors={len(errors)}")
        for e in errors[:5]:
            print(f"  ERROR step={e[0]} player={e[1]}: {e[2]}")
