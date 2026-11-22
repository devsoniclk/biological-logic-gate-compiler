"""Continuous steady-state Hill kinetics modeling and signal evaluation."""

import math

from biological_logic_compiler.library import get_crosstalk_coefficient
from biological_logic_compiler.models import (
    CircuitGraph,
    RepressorParam,
    SimulationResult,
    TruthTableSummary,
)


class HillKineticsSolver:
    """Evaluates non-linear transcription factor binding and promoter signal propagation."""
    def __init__(
        self,
        repressor_library: dict[str, RepressorParam],
        high_input_rpu: float = 3.5,
        low_input_rpu: float = 0.02,
        high_threshold_cutoff: float = 0.8,
        low_threshold_cutoff: float = 0.3,
    ):
        self.library = repressor_library
        self.high_input_rpu = high_input_rpu
        self.low_input_rpu = low_input_rpu
        self.high_threshold_cutoff = high_threshold_cutoff
        self.low_threshold_cutoff = low_threshold_cutoff

    def compute_transfer_function(
        self,
        repressor: RepressorParam,
        input_flux: float,
        cross_interference: float = 0.0,
    ) -> float:
        """Compute steady-state promoter activity (RPU) under cumulative input repression."""
        effective_input = input_flux + cross_interference
        if effective_input <= 0.0:
            return repressor.y_max

        # Hill equation: y = y_min + (y_max - y_min) / (1 + (x / K)^n)
        ratio = effective_input / repressor.k_threshold
        try:
            power = math.pow(ratio, repressor.hill_coefficient)
            y = repressor.y_min + (repressor.y_max - repressor.y_min) / (1.0 + power)
        except OverflowError:
            y = repressor.y_min
        return max(repressor.y_min, min(repressor.y_max, y))

    def simulate_state(
        self,
        circuit: CircuitGraph,
        boolean_inputs: dict[str, bool],
    ) -> SimulationResult:
        """Simulate analog circuit expression levels for a specific Boolean input combination."""
        expressions: dict[str, float] = {}

        # 1. Initialize primary inputs
        input_rpus: dict[str, float] = {}
        for var_name, state in boolean_inputs.items():
            in_node_id = f"in_{var_name}"
            val = self.high_input_rpu if state else self.low_input_rpu
            expressions[in_node_id] = val
            input_rpus[var_name] = val

        # 2. Propagate through topological order
        topo_order = circuit.get_topological_order()
        for node_id in topo_order:
            node = circuit.nodes[node_id]
            if node.gate_type == "INPUT":
                continue

            if node.gate_type == "OUTPUT":
                parent_id = node.inputs[0]
                expressions[node_id] = expressions[parent_id]
                continue

            # Compute additive flux across tandem promoters
            incoming_flux = sum(expressions[p_id] for p_id in node.inputs)

            # Compute cross-talk interference from active non-cognate repressors
            crosstalk_sum = 0.0
            if node.assigned_repressor:
                for other_id, other_node in circuit.nodes.items():
                    if other_id != node_id and other_node.assigned_repressor:
                        factor = get_crosstalk_coefficient(other_node.assigned_repressor, node.assigned_repressor)
                        if factor > 0 and other_id in expressions:
                            crosstalk_sum += factor * expressions[other_id]

            repressor_name = node.assigned_repressor or "TetR"
            repressor = self.library.get(repressor_name)
            if not repressor:
                raise ValueError(f"Assigned repressor '{repressor_name}' not in library.")

            out_rpu = self.compute_transfer_function(repressor, incoming_flux, crosstalk_sum)
            expressions[node_id] = out_rpu

        output_rpu = expressions[circuit.primary_output]
        is_high = output_rpu >= self.high_threshold_cutoff

        # Calculate noise margin
        if is_high:
            noise_margin = output_rpu - self.high_threshold_cutoff
        else:
            noise_margin = self.low_threshold_cutoff - output_rpu

        return SimulationResult(
            input_values=input_rpus,
            node_expressions=expressions,
            output_expression=output_rpu,
            interpreted_boolean=is_high,
            noise_margin=noise_margin,
        )

    def evaluate_truth_table(
        self,
        circuit: CircuitGraph,
        expected_ast=None,
    ) -> TruthTableSummary:
        """Test and verify all input permutations against expected Boolean logic."""
        import itertools
        vars_sorted = sorted(circuit.primary_inputs)
        combinations = list(itertools.product([False, True], repeat=len(vars_sorted)))

        states: list[SimulationResult] = []
        is_all_valid = True
        min_nm = float("inf")
        high_signals: list[float] = []
        low_signals: list[float] = []

        for combo in combinations:
            env = dict(zip(vars_sorted, combo))
            res = self.simulate_state(circuit, env)
            states.append(res)
            min_nm = min(min_nm, res.noise_margin)

            if res.interpreted_boolean:
                high_signals.append(res.output_expression)
            else:
                low_signals.append(res.output_expression)

            if expected_ast is not None:
                expected_bool = expected_ast.evaluate(env)
                if res.interpreted_boolean != expected_bool:
                    is_all_valid = False

        avg_high = sum(high_signals) / max(1, len(high_signals)) if high_signals else self.high_threshold_cutoff
        avg_low = sum(low_signals) / max(1, len(low_signals)) if low_signals else self.low_threshold_cutoff
        signal_ratio = max(1.001, avg_high / max(0.001, avg_low))
        snr_db = 10.0 * math.log10(signal_ratio)

        return TruthTableSummary(
            states=states,
            is_boolean_valid=is_all_valid,
            min_noise_margin=min_nm,
            snr_db=snr_db,
            max_crosstalk_interference=0.05,
        )
