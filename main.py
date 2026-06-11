"""Root submission entry — re-exports Phase 7 agent."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "phase7"))
from agent import agent

__all__ = ["agent"]
