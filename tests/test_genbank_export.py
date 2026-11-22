"""Tests for GenBank flat-file construct export."""

from biological_logic_compiler.decomposition import decompose_to_nor_graph
from biological_logic_compiler.genbank_export import export_to_genbank
from biological_logic_compiler.library import get_default_repressor_library
from biological_logic_compiler.optimizer import assign_repressors_to_circuit
from biological_logic_compiler.parser import parse_boolean_expression


def test_genbank_emission():
    lib = get_default_repressor_library()
    ast = parse_boolean_expression("A AND B")
    circ = decompose_to_nor_graph(ast, circuit_name="TestAndPlasmid")
    circ = assign_repressors_to_circuit(circ, lib, ast=ast)

    gb = export_to_genbank(circ, lib)
    assert "LOCUS" in gb
    assert "FEATURES" in gb
    assert "ORIGIN" in gb
    assert "promoter" in gb
    assert "CDS" in gb
    assert "terminator" in gb
    assert "//" in gb
