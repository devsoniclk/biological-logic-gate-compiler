"""Data models for biological logic circuits and kinetic parameters."""

from pydantic import BaseModel, Field


class RepressorParam(BaseModel):
    """Biophysical kinetic parameters for an engineered transcriptional repressor."""
    name: str = Field(description="Unique symbol or identifier of repressor protein")
    y_min: float = Field(description="Basal promoter activity in Relative Promoter Units (RPU)")
    y_max: float = Field(description="Maximal unrepressed promoter activity (RPU)")
    k_threshold: float = Field(description="Repression threshold concentration (RPU)")
    hill_coefficient: float = Field(description="Cooperative binding Hill coefficient")
    promoter_seq: str = Field(default="TTGACAATTAATCATCGGCTCGTATAATGTGTGGA", description="Operator promoter sequence")
    rbs_seq: str = Field(default="AAGGAGGTGTT", description="Ribosome binding site sequence")
    cds_seq: str = Field(default="ATGAAAACCTCCTGA", description="Coding sequence")
    terminator_seq: str = Field(default="CCAGGCATCAAATAAAACGAAAGGCTCAGTCGAAAGACTGGGCCTTTCGTTTTATCTGTTGTTTGTCGGTGAACGCTCTC", description="Transcriptional terminator sequence")


class LogicNode(BaseModel):
    """Topological node representing an in-silico logic gate in the regulatory network."""
    node_id: str
    gate_type: str = Field(description="Gate classification: INPUT, NOR, NOT, or OUTPUT")
    inputs: list[str] = Field(default_factory=list, description="IDs of driving upstream nodes")
    assigned_repressor: str | None = None
    output_signal: float = 0.0


class CircuitGraph(BaseModel):
    """Directed acyclic graph of interconnected biological logic gates."""
    circuit_name: str
    primary_inputs: list[str]
    primary_output: str
    nodes: dict[str, LogicNode]

    def get_topological_order(self) -> list[str]:
        """Return node IDs sorted in topological dependency order."""
        visited: dict[str, bool] = {}
        order: list[str] = []

        def dfs(node_id: str):
            visited[node_id] = True
            for parent_id in self.nodes[node_id].inputs:
                if not visited.get(parent_id, False):
                    dfs(parent_id)
            order.append(node_id)

        dfs(self.primary_output)
        return order


class SimulationResult(BaseModel):
    """Results from evaluating circuit steady-state expression across an input state."""
    input_values: dict[str, float]
    node_expressions: dict[str, float]
    output_expression: float
    interpreted_boolean: bool
    noise_margin: float


class TruthTableSummary(BaseModel):
    """Complete multi-state truth table verification report."""
    states: list[SimulationResult]
    is_boolean_valid: bool
    min_noise_margin: float
    snr_db: float
    max_crosstalk_interference: float
