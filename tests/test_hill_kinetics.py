"""Tests for continuous steady-state Hill kinetics solver."""

import pytest

from biological_logic_compiler.decomposition import decompose_to_nor_graph
from biological_logic_compiler.hill_kinetics import HillKineticsSolver
from biological_logic_compiler.library import get_default_repressor_library
from biological_logic_compiler.parser import parse_boolean_expression


def test_hill_transfer_extremes():
    lib = get_default_repressor_library()
    solver = HillKineticsSolver(repressor_library=lib)
    tetr = lib["TetR"]

    # Zero input -> y_max
    out_zero = solver.compute_transfer_function(tetr, 0.0)
    assert pytest.approx(out_zero, 0.01) == tetr.y_max

    # Massive input -> y_min
    out_inf = solver.compute_transfer_function(tetr, 100.0)
    assert pytest.approx(out_inf, 0.01) == tetr.y_min

    # Threshold input (x = K) -> (y_max + y_min) / 2
    out_k = solver.compute_transfer_function(tetr, tetr.k_threshold)
    expected_mid = tetr.y_min + (tetr.y_max - tetr.y_min) / 2.0
    assert pytest.approx(out_k, 0.01) == expected_mid

def test_single_not_gate_simulation():
    lib = get_default_repressor_library()
    solver = HillKineticsSolver(repressor_library=lib)
    ast = parse_boolean_expression("NOT(A)")
    circ = decompose_to_nor_graph(ast)
    # Assign TetR
    for node in circ.nodes.values():
        if node.gate_type in ("NOR", "NOT"):
            node.assigned_repressor = "TetR"

    res_off = solver.simulate_state(circ, {"A": False})
    assert res_off.interpreted_boolean is True
    assert res_off.output_expression > 1.0

    res_on = solver.simulate_state(circ, {"A": True})
    assert res_on.interpreted_boolean is False
    assert res_on.output_expression < 0.3
