"""FastMCP JSON-RPC stdio tool execution server."""

import json
import sys
from typing import Any

from biological_logic_compiler.decomposition import decompose_to_nor_graph
from biological_logic_compiler.genbank_export import export_to_genbank
from biological_logic_compiler.hill_kinetics import HillKineticsSolver
from biological_logic_compiler.library import get_default_repressor_library
from biological_logic_compiler.optimizer import assign_repressors_to_circuit
from biological_logic_compiler.parser import parse_boolean_expression
from biological_logic_compiler.sbol_export import export_to_sbol3_json


class BioCompilerMCPServer:
    """FastMCP stdio server exposing biological circuit compilation and simulation tools."""
    def __init__(self):
        self.library = get_default_repressor_library()
        self.solver = HillKineticsSolver(repressor_library=self.library)

    def compile_circuit(self, expression: str, circuit_name: str = "BioCircuit") -> dict[str, Any]:
        """Compile a Boolean logic expression into a physical genetic circuit design."""
        ast = parse_boolean_expression(expression)
        raw_circuit = decompose_to_nor_graph(ast, circuit_name=circuit_name)
        optimized_circuit = assign_repressors_to_circuit(raw_circuit, self.library, ast=ast)
        truth_table = self.solver.evaluate_truth_table(optimized_circuit, expected_ast=ast)

        gates_info = {}
        for nid, node in optimized_circuit.nodes.items():
            if node.gate_type in ("NOR", "NOT"):
                gates_info[nid] = {
                    "type": node.gate_type,
                    "inputs": node.inputs,
                    "assigned_repressor": node.assigned_repressor,
                }

        return {
            "circuit_name": circuit_name,
            "expression": expression,
            "inputs": optimized_circuit.primary_inputs,
            "gate_count": len(gates_info),
            "gates": gates_info,
            "boolean_verified": truth_table.is_boolean_valid,
            "min_noise_margin_rpu": round(truth_table.min_noise_margin, 4),
            "snr_db": round(truth_table.snr_db, 2),
            "states_evaluated": len(truth_table.states),
        }

    def simulate_circuit_inputs(
        self,
        expression: str,
        input_states: dict[str, bool],
    ) -> dict[str, Any]:
        """Simulate analog steady-state expression across all nodes for a specific input state."""
        ast = parse_boolean_expression(expression)
        raw_circuit = decompose_to_nor_graph(ast)
        circuit = assign_repressors_to_circuit(raw_circuit, self.library, ast=ast)
        res = self.solver.simulate_state(circuit, input_states)

        return {
            "inputs": res.input_values,
            "output_expression_rpu": round(res.output_expression, 4),
            "interpreted_boolean": res.interpreted_boolean,
            "noise_margin": round(res.noise_margin, 4),
            "node_signals": {k: round(v, 4) for k, v in res.node_expressions.items()},
        }

    def get_library(self) -> dict[str, Any]:
        """Retrieve all characterized biophysical parameters of orthogonal repressors."""
        return {
            name: {
                "y_min_rpu": u.y_min,
                "y_max_rpu": u.y_max,
                "k_threshold_rpu": u.k_threshold,
                "hill_coefficient": u.hill_coefficient,
                "promoter_len_bp": len(u.promoter_seq),
                "cds_len_bp": len(u.cds_seq),
            }
            for name, u in self.library.items()
        }

    def export_sbol3(self, expression: str, circuit_name: str = "BioCircuit") -> dict[str, Any]:
        """Generate SBOL3 JSON-LD biological construct specification."""
        ast = parse_boolean_expression(expression)
        circuit = decompose_to_nor_graph(ast, circuit_name=circuit_name)
        circuit = assign_repressors_to_circuit(circuit, self.library, ast=ast)
        return export_to_sbol3_json(circuit, self.library)

    def export_genbank_file(self, expression: str, circuit_name: str = "BioCircuit") -> str:
        """Generate annotated GenBank construct sequence file."""
        ast = parse_boolean_expression(expression)
        circuit = decompose_to_nor_graph(ast, circuit_name=circuit_name)
        circuit = assign_repressors_to_circuit(circuit, self.library, ast=ast)
        return export_to_genbank(circuit, self.library)


def run_stdio_server():
    """Stdio JSON-RPC loop handling FastMCP tool calls."""
    server = BioCompilerMCPServer()
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            req_id = req.get("id")
            method = req.get("method")
            params = req.get("params", {})

            if method == "compile_circuit":
                res = server.compile_circuit(params["expression"], params.get("circuit_name", "BioCircuit"))
            elif method == "simulate_circuit_inputs":
                res = server.simulate_circuit_inputs(params["expression"], params["input_states"])
            elif method == "get_library":
                res = server.get_library()
            elif method == "export_sbol3":
                res = server.export_sbol3(params["expression"], params.get("circuit_name", "BioCircuit"))
            elif method == "export_genbank_file":
                res = server.export_genbank_file(params["expression"], params.get("circuit_name", "BioCircuit"))
            else:
                res = {"error": f"Unknown method {method}"}

            out = json.dumps({"jsonrpc": "2.0", "id": req_id, "result": res})
            sys.stdout.write(out + "\n")
            sys.stdout.flush()
        except Exception as e:  # noqa: BLE001
            out = json.dumps({"jsonrpc": "2.0", "error": str(e)})
            sys.stdout.write(out + "\n")
            sys.stdout.flush()
