"""ASRA scientific reasoning loop for Orbit Wars."""
from simulation import simulate

# ASRA hypotheses → policy clusters to test via simulation
HYPOTHESES = {
    "economy": {
        "theory": "High-production neutrals compound over 500 turns",
        "policies": ["expand_neutrals", "conservative"],
    },
    "aggression": {
        "theory": "Eliminating weakest enemy reduces future threats",
        "policies": ["snipe_weakest", "expand_all"],
    },
    "comets": {
        "theory": "Temporary comet captures boost ship count cheaply",
        "policies": ["comet_rush", "expand_neutrals"],
    },
    "consolidation": {
        "theory": "Reinforcing production centers before expanding wins",
        "policies": ["reinforce_home", "conservative"],
    },
    "balanced": {
        "theory": "Mixed expansion across all targets is robust in FFA",
        "policies": ["expand_all", "expand_neutrals"],
    },
}

SIM_DEPTH = 15


def experiment(hypothesis_name, build_moves_fn, world, planets, sim_ctx):
    """ASRA Experiment: simulate a hypothesis and return (score, moves)."""
    policies = HYPOTHESES[hypothesis_name]["policies"]
    sim_planets, sim_fleets, av, init_map, player = sim_ctx

    best_score = float("-inf")
    best_moves = []

    for policy in policies:
        moves = build_moves_fn(planets, world, policy)
        score = simulate(sim_planets, sim_fleets, player, init_map, av, moves, SIM_DEPTH)
        if score > best_score:
            best_score = score
            best_moves = moves

    return best_score, best_moves, hypothesis_name


def reason(build_moves_fn, world, planets, sim_ctx):
    """
    ASRA loop: Observe (done) → Hypothesize → Experiment → Analyze → return best Act.
    """
    results = []
    for name in HYPOTHESES:
        score, moves, hname = experiment(name, build_moves_fn, world, planets, sim_ctx)
        results.append((score, moves, hname))

    results.sort(key=lambda x: x[0], reverse=True)
    return results[0][1]  # opening moves of best hypothesis
