"""SBOL3 JSON-LD graph serialization for synthetic regulatory designs."""

from typing import Any

from biological_logic_compiler.models import CircuitGraph, RepressorParam


def export_to_sbol3_json(
    circuit: CircuitGraph,
    library: dict[str, RepressorParam],
) -> dict[str, Any]:
    """Serialize the compiled genetic circuit topology into valid SBOL3 JSON-LD format."""
    base_uri = f"https://devsoniclk.github.io/sbol3/{circuit.circuit_name}"

    graph: dict[str, Any] = {
        "@context": {
            "sbol": "http://sbols.org/v3#",
            "edam": "http://edamontology.org/",
            "so": "http://identifiers.org/so/",
        },
        "@id": f"{base_uri}/Component/{circuit.circuit_name}",
        "@type": "sbol:Component",
        "sbol:displayId": circuit.circuit_name,
        "sbol:name": f"Genetic Logic Circuit: {circuit.circuit_name}",
        "sbol:type": "so:SO:0000804",  # engineered region
        "sbol:hasFeature": [],
        "sbol:hasConstraint": [],
    }

    feature_order = []
    for node_id, node in circuit.nodes.items():
        if node.gate_type in ("NOR", "NOT") and node.assigned_repressor:
            repressor = library[node.assigned_repressor]
            tu_id = f"{base_uri}/Feature/{node_id}_{node.assigned_repressor}"
            tu_feature = {
                "@id": tu_id,
                "@type": "sbol:SubComponent",
                "sbol:displayId": f"{node_id}_{node.assigned_repressor}",
                "sbol:role": "so:SO:0000804",
                "sbol:name": f"Transcriptional Unit {node.assigned_repressor} for Gate {node_id}",
                "sbol:promoterSeq": repressor.promoter_seq,
                "sbol:rbsSeq": repressor.rbs_seq,
                "sbol:cdsSeq": repressor.cds_seq,
                "sbol:terminatorSeq": repressor.terminator_seq,
            }
            graph["sbol:hasFeature"].append(tu_feature)
            feature_order.append(tu_id)

    # Add linear layout constraints
    for i in range(len(feature_order) - 1):
        graph["sbol:hasConstraint"].append({
            "@type": "sbol:Constraint",
            "sbol:restriction": "sbol:precedes",
            "sbol:subject": feature_order[i],
            "sbol:object": feature_order[i + 1],
        })

    return graph
