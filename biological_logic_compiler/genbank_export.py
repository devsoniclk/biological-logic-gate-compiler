"""GenBank sequence formatting for DNA foundry assembly."""

from datetime import datetime

from biological_logic_compiler.models import CircuitGraph, RepressorParam


def format_sequence(seq: str, line_len: int = 60) -> str:
    """Format raw DNA nucleotides into standard GenBank origin block format."""
    lines = []
    seq_lower = seq.lower()
    for i in range(0, len(seq_lower), line_len):
        chunk = seq_lower[i:i + line_len]
        # Split into 10-base blocks
        blocks = [chunk[j:j + 10] for j in range(0, len(chunk), 10)]
        line_str = f"{i + 1:>9} " + " ".join(blocks)
        lines.append(line_str)
    return "\n".join(lines)


def export_to_genbank(
    circuit: CircuitGraph,
    library: dict[str, RepressorParam],
) -> str:
    """Generate a standard GenBank flat-file (.gb) string describing the synthesized plasmid construct."""
    features_text = ""
    dna_seq = ""
    current_pos = 1

    scar = "TACTAGAG"  # BioBrick standard scar

    for node_id, node in circuit.nodes.items():
        if node.gate_type in ("NOR", "NOT") and node.assigned_repressor:
            rep = library[node.assigned_repressor]

            # 1. Promoter
            p_start = current_pos
            p_end = p_start + len(rep.promoter_seq) - 1
            features_text += f"     promoter        {p_start}..{p_end}\n"
            features_text += f'                     /gene="{rep.name}"\n'
            features_text += f'                     /label="p_{rep.name}"\n'
            features_text += f'                     /note="Gate {node_id} operator promoter"\n'
            dna_seq += rep.promoter_seq
            current_pos = p_end + 1

            # Scar
            dna_seq += scar
            current_pos += len(scar)

            # 2. RBS
            rbs_start = current_pos
            rbs_end = rbs_start + len(rep.rbs_seq) - 1
            features_text += f"     RBS             {rbs_start}..{rbs_end}\n"
            features_text += f'                     /gene="{rep.name}"\n'
            features_text += f'                     /label="RBS_{rep.name}"\n'
            dna_seq += rep.rbs_seq
            current_pos = rbs_end + 1

            # 3. CDS
            cds_start = current_pos
            cds_end = cds_start + len(rep.cds_seq) - 1
            features_text += f"     CDS             {cds_start}..{cds_end}\n"
            features_text += f'                     /gene="{rep.name}"\n'
            features_text += f'                     /label="{rep.name}_CDS"\n'
            dna_seq += rep.cds_seq
            current_pos = cds_end + 1

            # 4. Terminator
            term_start = current_pos
            term_end = term_start + len(rep.terminator_seq) - 1
            features_text += f"     terminator      {term_start}..{term_end}\n"
            features_text += f'                     /gene="{rep.name}"\n'
            features_text += f'                     /label="term_{rep.name}"\n'
            dna_seq += rep.terminator_seq
            current_pos = term_end + 1

    total_len = len(dna_seq)
    today = datetime.now().strftime("%d-%b-%Y").upper()

    header = f"""LOCUS       {circuit.circuit_name[:16]:<16} {total_len:>7} bp    DNA     linear   SYN {today}
DEFINITION  Synthetic gene regulatory circuit: {circuit.circuit_name}.
ACCESSION   SYN_{circuit.circuit_name}
VERSION     SYN_{circuit.circuit_name}.1
SOURCE      Synthetic construct
  ORGANISM  Synthetic construct
            Biochemically engineered microbial chassis.
FEATURES             Location/Qualifiers
{features_text}ORIGIN
{format_sequence(dna_seq)}
//
"""
    return header
