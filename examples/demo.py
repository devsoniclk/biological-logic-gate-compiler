"""Demonstration of logic gate compilation and steady-state kinetics."""

from biological_logic_compiler import (
    HillKineticsSolver,
    assign_repressors_to_circuit,
    decompose_to_nor_graph,
    export_to_genbank,
    get_default_repressor_library,
    parse_boolean_expression,
)


def main():
    expr = "A AND NOT(B)"
    print(f"Compiling expression: {expr}")
    ast = parse_boolean_expression(expr)
    raw_circuit = decompose_to_nor_graph(ast, circuit_name="DemoANDNOT")
    library = get_default_repressor_library()
    circuit = assign_repressors_to_circuit(raw_circuit, library, ast=ast)

    solver = HillKineticsSolver(repressor_library=library)
    summary = solver.evaluate_truth_table(circuit, expected_ast=ast)

    print(f"Gates count: {len(circuit.nodes)}")
    print(f"Boolean verification: {'PASSED' if summary.is_boolean_valid else 'FAILED'}")
    print(f"Min noise margin: {summary.min_noise_margin:.4f} RPU | SNR: {summary.snr_db:.2f} dB")

    gb = export_to_genbank(circuit, library)
    print(f"GenBank construct size: {len(gb)} chars")

if __name__ == "__main__":
    main()
