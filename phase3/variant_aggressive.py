"""Phase 3 alternate submission — aggressive expand/attack variant."""
from agent import decide


def agent(obs):
    return decide(obs, aggressive=True)
