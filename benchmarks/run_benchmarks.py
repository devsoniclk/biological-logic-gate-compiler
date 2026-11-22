"""Performance and gate-depth synthesis benchmark suite."""

import time

from biological_logic_compiler import (
    HillKineticsSolver,
    assign_repressors_to_circuit,
    decompose_to_nor_graph,
    get_default_repressor_library,
    parse_boolean_expression,
)

BENCHMARKS = [
    ("Inverter", "NOT(A)"),
    ("NOR Gate", "A NOR B"),
    ("NAND Gate", "A NAND B"),
    ("AND Gate", "A AND B"),
    ("OR Gate", "A OR B"),
    ("XOR Gate", "A XOR B"),
    ("2-to-1 Multiplexer", "(A AND S) OR (B AND NOT(S))"),
    ("Majority Voter 3-in", "(A AND B) OR (B AND C) OR (A AND C)"),
]

def run():
    library = get_default_repressor_library()
    solver = HillKineticsSolver(repressor_library=library)

    print(f"{'Benchmark Circuit':<24} | {'Gates':<6} | {'Synthesis (ms)':<14} | {'Valid':<6} | {'SNR (dB)':<8}")
    print("-" * 70)

    for name, expr in BENCHMARKS:
        t0 = time.perf_counter()
        ast = parse_boolean_expression(expr)
        raw_circ = decompose_to_nor_graph(ast, circuit_name=name.replace(" ", "_"))
        opt_circ = assign_repressors_to_circuit(raw_circ, library, ast=ast)
        t_ms = (time.perf_counter() - t0) * 1000.0

        summary = solver.evaluate_truth_table(opt_circ, expected_ast=ast)
        valid_str = "YES" if summary.is_boolean_valid else "NO"
        print(f"{name:<24} | {len(opt_circ.nodes):<6} | {t_ms:<14.2f} | {valid_str:<6} | {summary.snr_db:<8.2f}")

if __name__ == "__main__":
    run()
