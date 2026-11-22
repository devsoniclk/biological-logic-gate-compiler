# Biological Logic Gate & Gene Regulatory Network (GRN) Compiler

[![CI](https://github.com/devsoniclk/biological-logic-gate-compiler/actions/workflows/ci.yml/badge.svg)](https://github.com/devsoniclk/biological-logic-gate-compiler/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

Production-grade computational synthetic biology CAD engine translating formal Boolean logic expressions into living Gene Regulatory Networks (GRNs) in microbial chassis (e.g., *Escherichia coli*). Implements universal NOR decomposition, continuous non-linear Hill equation transfer function modeling, dynamic range matching, transcriptional crosstalk mitigation, and automated emission of SBOL3 (Synthetic Biology Open Language) and GenBank sequence files.

---

## Key Capabilities

1. **Formal Boolean Parsing & AST Generation**:
   - Tokenizes and parses arbitrary Boolean logic strings with binary and unary operations (`AND`, `OR`, `NOT`, `XOR`, `NAND`, `NOR`, `XNOR`).
   - Produces clean Abstract Syntax Trees (ASTs) with operator precedence and associativity validation.

2. **Universal NOR Decomposition**:
   - Transforms arbitrary Boolean ASTs into topological Directed Acyclic Graphs (DAGs) composed exclusively of 2-input physical NOR units and inverters.
   - Leverages synthetic biology tandem promoters where physical flux summation computes $x_{\text{total}} = x_1 + x_2$, enabling native biological NOR logic.

3. **Continuous Biophysical Hill Kinetics**:
   - Models non-linear transcriptional repressor saturation using the generalized Hill equation:
     $$y = y_{\text{min}} + \frac{y_{\text{max}} - y_{\text{min}}}{1 + \left(\frac{x}{K}\right)^n}$$
   - Simulates continuous signal propagation in Relative Promoter Units (RPU) across arbitrary multi-stage cascades.
   - Computes noise margins, on/off dynamic ranges, and boolean truth-table fidelity scores.

4. **Orthogonal Repressor Library & Optimization**:
   - Built-in characterized biophysical library of orthogonal repressor proteins (e.g., TetR, LacI, PhlF, AmeRs, BetI, QacR).
   - Dynamic range matching algorithm that assigns repressors to minimize signal degradation, prevent cascade attenuation, and reduce transcriptional crosstalk.

5. **Standardized Synthetic Biology File Emission**:
   - **SBOL3 (Synthetic Biology Open Language)**: Emits compliant JSON representations with `Component`, `SubComponent`, and `Sequence` elements.
   - **GenBank**: Generates standard multi-feature GenBank flat files annotating promoters, ribosome binding sites (RBS), coding sequences (CDS), and transcriptional terminators.

6. **FastMCP Server & Rich CLI**:
   - FastMCP stdio server exposing tools for Boolean synthesis, circuit evaluation, and sequence export to AI agents.
   - Rich CLI (`bio-compiler`) for interactive compilation, truth table simulation, and genetic circuit visual inspection.

---

## Mathematical Formulation

### 1. Transcriptional Repressor Hill Transfer Function
For a transcriptional repressor binding to an engineered operator promoter, output transcription activity $y$ (in Relative Promoter Units, RPU) as a function of upstream repressor input activity $x$ is:

$$y = y_{\text{min}} + \frac{y_{\text{max}} - y_{\text{min}}}{1 + \left(\frac{x}{K}\right)^n}$$

Where:
- $y_{\text{min}}$: Leaky basal transcription rate under saturated repression.
- $y_{\text{max}}$: Maximal unrepressed promoter initiation rate.
- $K$: Repression threshold concentration achieving half-maximal repression ($50\%$).
- $n$: Hill cooperativity coefficient reflecting repressor multimerization and operator site occupancy.

### 2. Tandem Promoter NOR Topology
In living microbial hosts, placing two independent operator promoters in tandem upstream of a single repressor coding sequence produces additive transcriptional flux:

$$x_{\text{eff}} = x_1 + x_2$$

Driving the downstream repressor yields the physical NOR transfer function:

$$y_{\text{NOR}}(x_1, x_2) = y_{\text{min}} + \frac{y_{\text{max}} - y_{\text{min}}}{1 + \left(\frac{x_1 + x_2}{K}\right)^n}$$

### 3. Noise Margin & Dynamic Range Criteria
Signal restoration across consecutive gate layers requires:

$$\text{NM}_{\text{HIGH}} = y_{\text{HIGH}} - x_{\text{threshold}}^{\text{ON}} > 0$$
$$\text{NM}_{\text{LOW}} = x_{\text{threshold}}^{\text{OFF}} - y_{\text{LOW}} > 0$$

Circuits scoring positive noise margins at every stage prevent digital state collapse into intermediate analog regimes.

---

## Installation

```bash
git clone https://github.com/devsoniclk/biological-logic-gate-compiler.git
cd biological-logic-gate-compiler
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

---

## Quick Start

### Python API

```python
from biological_logic_compiler import (
    parse_boolean_expression,
    decompose_to_nor_graph,
    HillKineticsSolver,
    get_default_repressor_library,
    assign_repressors_to_circuit,
    export_to_genbank,
    export_to_sbol3_json,
)

# 1. Parse Boolean expression and synthesize universal NOR circuit
expression = "(A AND B) OR (NOT C)"
ast = parse_boolean_expression(expression)
circuit = decompose_to_nor_graph(ast, circuit_name="SensorCircuit")

# 2. Assign optimal orthogonal repressors from characterized biophysical library
library = get_default_repressor_library()
assigned_circuit = assign_repressors_to_circuit(circuit, library)

# 3. Simulate continuous non-linear Hill kinetics across all input combinations
solver = HillKineticsSolver(assigned_circuit, library)
truth_table = solver.evaluate_truth_table()

print(f"Synthesized Circuit: {circuit.circuit_name}")
print(f"Total Nodes: {len(circuit.nodes)}")
print(f"Boolean Fidelity Score: {truth_table.fidelity_score:.2%}")

for row in truth_table.rows:
    print(f"Inputs {row.input_values} -> Predicted RPU: {row.output_rpu:.4f} (State: {row.digital_state})")

# 4. Export physical construct sequence
genbank_record = export_to_genbank(assigned_circuit, library)
with open("sensor_circuit.gb", "w") as f:
    f.write(genbank_record)
```

---

## Command Line Interface (CLI)

The package provides the `bio-compiler` CLI:

```bash
# Compile and evaluate a Boolean expression
bio-compiler compile "(A AND B) OR (NOT C)"

# Simulate truth table with rich visual tables
bio-compiler simulate --expr "A XOR B"

# Export genetic construct to GenBank or SBOL3
bio-compiler export --expr "A AND B" --format genbank --output circuit.gb
bio-compiler export --expr "A AND B" --format sbol3 --output circuit.sbol.json

# Inspect available orthogonal repressor library
bio-compiler library
```

---

## Model Context Protocol (MCP) Server

Launch the FastMCP JSON-RPC 2.0 stdio server:

```bash
uv run python -m biological_logic_compiler.server
```

### Supported MCP Tools:
- `compile_circuit(expression: str, circuit_name: str)`: Decomposes Boolean logic into NOR circuit topology.
- `simulate_circuit(expression: str)`: Runs continuous Hill kinetics and evaluates truth table SNR.
- `list_repressor_library()`: Returns available orthogonal repressor biophysical parameters.
- `export_circuit_design(expression: str, format: str)`: Generates SBOL3 JSON or GenBank sequence format.

---

## Architecture & Project Structure

```
biological-logic-gate-compiler/
├── .github/workflows/ci.yml       # Automated GitHub Actions test & lint CI
├── biological_logic_compiler/
│   ├── __init__.py                # Public API entrypoint
│   ├── models.py                  # Pydantic data schemas (RepressorParam, CircuitGraph, LogicNode)
│   ├── parser.py                  # Boolean tokenization & recursive AST parser
│   ├── decomposition.py           # Universal NOR & tandem promoter DAG synthesizer
│   ├── hill_kinetics.py           # Non-linear Hill equation transfer solver & simulation
│   ├── library.py                 # Characterized library of orthogonal repressors (TetR, LacI, etc.)
│   ├── optimizer.py               # Signal matching & dynamic range optimization
│   ├── sbol_export.py             # SBOL3 synthetic biology standard serialization
│   ├── genbank_export.py          # GenBank flat file sequence generator
│   ├── cli.py                     # Rich-powered command-line interface
│   └── server.py                  # FastMCP tool server for AI agents
├── tests/                         # Comprehensive pytest test suite (100% pass)
├── pyproject.toml                 # Modern uv/hatchling packaging configuration
└── README.md                      # Mathematical formulation & documentation
```

---

## Verification & Testing

Run the full automated test suite:

```bash
uv run pytest
```

Check code style and linting:

```bash
uv run ruff check .
```

---

## License

MIT License. Designed and authored by **Lakshitha Dananjaya** ([@devsoniclk](https://github.com/devsoniclk)).
Co-authored by **OpenBot**.
