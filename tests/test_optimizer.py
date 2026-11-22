"""Tests for repressor assignment optimizer."""

from biological_logic_compiler.decomposition import decompose_to_nor_graph
from biological_logic_compiler.hill_kinetics import HillKineticsSolver
from biological_logic_compiler.library import get_default_repressor_library
from biological_logic_compiler.optimizer import assign_repressors_to_circuit
from biological_logic_compiler.parser import parse_boolean_expression


def test_optimizer_assignment():
    lib = get_default_repressor_library()
    ast = parse_boolean_expression("A AND B")
    circ = decompose_to_nor_graph(ast)
    opt_circ = assign_repressors_to_circuit(circ, lib, ast=ast)

    for node in opt_circ.nodes.values():
        if node.gate_type in ("NOR", "NOT"):
            assert node.assigned_repressor in lib

    solver = HillKineticsSolver(repressor_library=lib)
    summary = solver.evaluate_truth_table(opt_circ, expected_ast=ast)
    assert summary.is_boolean_valid is True
    assert summary.min_noise_margin > 0.0
