"""Tests for universal NOR decomposition and topological graph generation."""

from biological_logic_compiler.decomposition import decompose_to_nor_graph
from biological_logic_compiler.parser import parse_boolean_expression


def test_decompose_inverter():
    ast = parse_boolean_expression("NOT(X)")
    circuit = decompose_to_nor_graph(ast, circuit_name="TestInv")
    assert circuit.circuit_name == "TestInv"
    assert "in_X" in circuit.nodes
    assert circuit.primary_output == "out_primary"
    topo = circuit.get_topological_order()
    assert len(topo) > 0

def test_decompose_nor():
    ast = parse_boolean_expression("A NOR B")
    circuit = decompose_to_nor_graph(ast)
    assert "in_A" in circuit.nodes
    assert "in_B" in circuit.nodes
    nor_gates = [n for n in circuit.nodes.values() if n.gate_type == "NOR"]
    assert len(nor_gates) >= 1

def test_decompose_composite_operations():
    for expr in ["A AND B", "A OR B", "A NAND B", "A XOR B", "A XNOR B"]:
        ast = parse_boolean_expression(expr)
        circ = decompose_to_nor_graph(ast)
        assert circ.primary_output in circ.nodes
        assert len(circ.primary_inputs) == 2
