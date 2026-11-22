"""Heuristic assignment of orthogonal repressors to circuit gates."""

from biological_logic_compiler.hill_kinetics import HillKineticsSolver
from biological_logic_compiler.models import CircuitGraph, RepressorParam


def assign_repressors_to_circuit(
    circuit: CircuitGraph,
    library: dict[str, RepressorParam],
    ast=None,
) -> CircuitGraph:
    """Pair available biological repressors to gates to maximize noise margin and minimize crosstalk."""
    gates = [
        node_id for node_id, node in circuit.nodes.items()
        if node.gate_type in ("NOR", "NOT")
    ]
    repressor_names = list(library.keys())

    if len(gates) > len(repressor_names):
        # Repressor reuse required for large circuits
        pass

    solver = HillKineticsSolver(repressor_library=library)

    # Initial round-robin assignment
    for i, g_id in enumerate(gates):
        chosen = repressor_names[i % len(repressor_names)]
        circuit.nodes[g_id].assigned_repressor = chosen

    best_score = -1e9
    best_assignment = {g: circuit.nodes[g].assigned_repressor for g in gates}

    # Evaluate initial
    summary = solver.evaluate_truth_table(circuit, expected_ast=ast)
    valid_bonus = 1000.0 if summary.is_boolean_valid else -500.0
    best_score = valid_bonus + summary.min_noise_margin * 100.0 + summary.snr_db

    # Local hill climbing / permutation search for optimal pairing
    import itertools
    perm_candidates = list(itertools.islice(itertools.permutations(repressor_names, min(len(gates), len(repressor_names))), 40))
    for candidate in perm_candidates:
        for idx, g_id in enumerate(gates):
            circuit.nodes[g_id].assigned_repressor = candidate[idx % len(candidate)]

        cur_summary = solver.evaluate_truth_table(circuit, expected_ast=ast)
        cur_bonus = 1000.0 if cur_summary.is_boolean_valid else -500.0
        cur_score = cur_bonus + cur_summary.min_noise_margin * 100.0 + cur_summary.snr_db

        if cur_score > best_score:
            best_score = cur_score
            best_assignment = {g: circuit.nodes[g].assigned_repressor for g in gates}

    # Re-apply best configuration
    for g_id, rep_name in best_assignment.items():
        circuit.nodes[g_id].assigned_repressor = rep_name

    return circuit
