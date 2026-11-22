"""Command-line interface for the Biological Logic Gate Compiler."""

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from biological_logic_compiler.decomposition import decompose_to_nor_graph
from biological_logic_compiler.hill_kinetics import HillKineticsSolver
from biological_logic_compiler.library import get_default_repressor_library
from biological_logic_compiler.optimizer import assign_repressors_to_circuit
from biological_logic_compiler.parser import parse_boolean_expression

console = Console()


@click.group()
def cli():
    """Biological Logic Gate Compiler CLI."""


@cli.command()
@click.argument("expression", type=str)
@click.option("--name", default="BioCircuit", help="Name of synthesized genetic construct")
def compile(expression: str, name: str):
    """Compile Boolean logic into living Gene Regulatory Network."""
    console.print(Panel(f"[bold cyan]Compiling Boolean Logic:[/bold cyan] {expression}", title="BioCompiler"))

    library = get_default_repressor_library()
    ast = parse_boolean_expression(expression)
    circuit = decompose_to_nor_graph(ast, circuit_name=name)
    circuit = assign_repressors_to_circuit(circuit, library, ast=ast)

    solver = HillKineticsSolver(repressor_library=library)
    summary = solver.evaluate_truth_table(circuit, expected_ast=ast)

    # Gates table
    t_gates = Table(title="Synthesized Gate Assignments")
    t_gates.add_column("Node ID", style="cyan")
    t_gates.add_column("Type", style="green")
    t_gates.add_column("Inputs", style="yellow")
    t_gates.add_column("Assigned Repressor", style="magenta")

    for nid, node in circuit.nodes.items():
        if node.gate_type in ("NOR", "NOT"):
            t_gates.add_row(nid, node.gate_type, ", ".join(node.inputs), node.assigned_repressor or "None")
    console.print(t_gates)

    # Truth table
    t_truth = Table(title="Steady-State Kinetics Verification")
    for var in circuit.primary_inputs:
        t_truth.add_column(var, justify="center")
    t_truth.add_column("Output (RPU)", justify="right")
    t_truth.add_column("Logic", justify="center")
    t_truth.add_column("Margin (RPU)", justify="right")

    for st in summary.states:
        row = [str(int(st.input_values[v] > 1.0)) for v in circuit.primary_inputs]
        row.append(f"{st.output_expression:.4f}")
        logic_str = "[green]HIGH[/green]" if st.interpreted_boolean else "[red]LOW[/red]"
        row.append(logic_str)
        row.append(f"{st.noise_margin:+.4f}")
        t_truth.add_row(*row)
    console.print(t_truth)

    status = "[bold green]PASSED[/bold green]" if summary.is_boolean_valid else "[bold red]FAILED[/bold red]"
    console.print(f"\nVerification: {status} | Min Noise Margin: {summary.min_noise_margin:.4f} RPU | SNR: {summary.snr_db:.2f} dB")


@cli.command()
def library():
    """List available orthogonal transcriptional repressors."""
    lib = get_default_repressor_library()
    table = Table(title="Orthogonal Repressor Library")
    table.add_column("Symbol", style="cyan")
    table.add_column("y_min (RPU)", justify="right")
    table.add_column("y_max (RPU)", justify="right")
    table.add_column("K (RPU)", justify="right")
    table.add_column("Hill (n)", justify="right")

    for name, p in lib.items():
        table.add_row(name, f"{p.y_min:.4f}", f"{p.y_max:.2f}", f"{p.k_threshold:.2f}", f"{p.hill_coefficient:.2f}")
    console.print(table)


if __name__ == "__main__":
    cli()
