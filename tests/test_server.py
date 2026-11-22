"""Tests for FastMCP tool execution methods."""

from biological_logic_compiler.server import BioCompilerMCPServer


def test_server_compile_circuit():
    server = BioCompilerMCPServer()
    res = server.compile_circuit("A AND B", circuit_name="ServerTest")
    assert res["circuit_name"] == "ServerTest"
    assert res["boolean_verified"] is True
    assert res["gate_count"] >= 1
    assert res["snr_db"] > 0

def test_server_simulate_inputs():
    server = BioCompilerMCPServer()
    res = server.simulate_circuit_inputs("NOT(A)", {"A": True})
    assert res["interpreted_boolean"] is False
    assert res["output_expression_rpu"] < 0.5

def test_server_get_library():
    server = BioCompilerMCPServer()
    lib = server.get_library()
    assert "TetR" in lib
    assert "LacI" in lib

def test_server_export_files():
    server = BioCompilerMCPServer()
    sbol = server.export_sbol3("A OR B")
    assert "@type" in sbol
    gb = server.export_genbank_file("A OR B")
    assert "LOCUS" in gb
