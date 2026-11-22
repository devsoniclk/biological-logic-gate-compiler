"""Half-Adder composite circuit synthesis (Sum = A XOR B, Carry = A AND B)."""

from biological_logic_compiler import (
    HillKineticsSolver,
    assign_repressors_to_circuit,
    decompose_to_nor_graph,
    get_default_repressor_library,
    parse_boolean_expression,
)


def main():
    library = get_default_repressor_library()
    solver = HillKineticsSolver(repressor_library=library)

    # 1. XOR (Sum)
    ast_xor = parse_boolean_expression("A XOR B")
    circ_xor = decompose_to_nor_graph(ast_xor, circuit_name="HalfAdder_Sum")
    circ_xor = assign_repressors_to_circuit(circ_xor, library, ast=ast_xor)
    res_xor = solver.evaluate_truth_table(circ_xor, expected_ast=ast_xor)
    print(f"Sum (XOR) verification: {'PASSED' if res_xor.is_boolean_valid else 'FAILED'} (Min NM: {res_xor.min_noise_margin:.3f} RPU)")

    # 2. AND (Carry)
    ast_and = parse_boolean_expression("A AND B")
    circ_and = decompose_to_nor_graph(ast_and, circuit_name="HalfAdder_Carry")
    circ_and = assign_repressors_to_circuit(circ_and, library, ast=ast_and)
    res_and = solver.evaluate_truth_table(circ_and, expected_ast=ast_and)
    print(f"Carry (AND) verification: {'PASSED' if res_and.is_boolean_valid else 'FAILED'} (Min NM: {res_and.min_noise_margin:.3f} RPU)")

if __name__ == "__main__":
    main()
