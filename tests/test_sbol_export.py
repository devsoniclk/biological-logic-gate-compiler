"""Tests for SBOL3 JSON-LD biological construct export."""

from biological_logic_compiler.decomposition import decompose_to_nor_graph
from biological_logic_compiler.library import get_default_repressor_library
from biological_logic_compiler.optimizer import assign_repressors_to_circuit
from biological_logic_compiler.parser import parse_boolean_expression
from biological_logic_compiler.sbol_export import export_to_sbol3_json


def test_sbol3_emission():
    lib = get_default_repressor_library()
    ast = parse_boolean_expression("A OR B")
    circ = decompose_to_nor_graph(ast, circuit_name="TestOrCircuit")
    circ = assign_repressors_to_circuit(circ, lib, ast=ast)

    sbol = export_to_sbol3_json(circ, lib)
    assert sbol["@type"] == "sbol:Component"
    assert "sbol:hasFeature" in sbol
    assert len(sbol["sbol:hasFeature"]) > 0
    assert len(sbol["sbol:hasConstraint"]) >= len(sbol["sbol:hasFeature"]) - 1
