"""Root submission entry — re-exports Phase 6 agent."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "phase6"))
from agent import agent

__all__ = ["agent"]
