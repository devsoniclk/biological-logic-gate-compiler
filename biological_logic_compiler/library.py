"""Curated library of orthogonal transcriptional control units."""

from biological_logic_compiler.models import RepressorParam


def get_default_repressor_library() -> dict[str, RepressorParam]:
    """Return an orthogonal suite of well-characterized transcriptional repressors."""
    units = [
        RepressorParam(
            name="TetR",
            y_min=0.015,
            y_max=4.80,
            k_threshold=0.12,
            hill_coefficient=2.40,
            promoter_seq="TCCCTATCAGTGATAGAGATTGACATCCCTATCAGTGATAGAGATAATGAGCAC",
            rbs_seq="AAGGAGGTGTT",
            cds_seq="ATGTCCAGATTAGATAAAAGTAAAGTGATTAACAGCGCATTAGAGCTGCTTAATGAGGTCGGAATCGAAGGTTTAACAACCCGTAAACTCGCCCAGAAGCTAGGTGTA",
            terminator_seq="CCAGGCATCAAATAAAACGAAAGGCTCAGTCGAAAGACTGGGCCTTTCGTTTTATCTGTTGTTTGTCGGTGAACGCTCTC",
        ),
        RepressorParam(
            name="LacI",
            y_min=0.020,
            y_max=5.50,
            k_threshold=0.35,
            hill_coefficient=2.10,
            promoter_seq="AATTGTGAGCGCTCACAATTATGACAGAACTCACAATTAGTTAACGTAC",
            rbs_seq="AGGGAGACCAC",
            cds_seq="ATGGTGAAACCAGTAACGTTATACGATGTCGCAGAGTATGCCGGTGTCTCTTATCAGACCGTTTCCCGCGTGGTGAACCAGGCCAGCCACGTTTCTGCGAAAACGCGG",
            terminator_seq="CCAGGCATCAAATAAAACGAAAGGCTCAGTCGAAAGACTGGGCCTTTCGTTTTATCTGTTGTTTGTCGGTGAACGCTCTC",
        ),
        RepressorParam(
            name="PhlF",
            y_min=0.012,
            y_max=3.90,
            k_threshold=0.08,
            hill_coefficient=3.20,
            promoter_seq="TTATGATACGATGTTTCCCGGTTGACATATGATACGATGTTTCCCGAATGAGCAC",
            rbs_seq="AAGTAGGTGAA",
            cds_seq="ATGATGGCACGCACCACCCGCGTGGTTTCCGAAGCCCTGCTGGCCGACCTGGCAGGTCGTGAACAGGCCCTGCTGGACGCGTTACGCCGCCTGCCGGATGGCTGGCTG",
            terminator_seq="CCAGGCATCAAATAAAACGAAAGGCTCAGTCGAAAGACTGGGCCTTTCGTTTTATCTGTTGTTTGTCGGTGAACGCTCTC",
        ),
        RepressorParam(
            name="AmeRs",
            y_min=0.030,
            y_max=4.20,
            k_threshold=0.25,
            hill_coefficient=2.70,
            promoter_seq="CTAGATCAGTGATTACGCATTGACACTAGATCAGTGATTACGCAAATGAGCAC",
            rbs_seq="AAGGAGATTCC",
            cds_seq="ATGAAAACCGTTACCGTTCGTGAACTGCAGGATGCCCTGTCCCGCCGTCTGGGTCTGGACCCGGAACGCCTGGCCGATGTCTTTGCCCGTCTGCCGGATGTTCGCGCA",
            terminator_seq="CCAGGCATCAAATAAAACGAAAGGCTCAGTCGAAAGACTGGGCCTTTCGTTTTATCTGTTGTTTGTCGGTGAACGCTCTC",
        ),
        RepressorParam(
            name="BetI",
            y_min=0.025,
            y_max=4.00,
            k_threshold=0.18,
            hill_coefficient=2.90,
            promoter_seq="AGTGATAGAGATTGACACAGTGATAGAGATAATGAGCAC",
            rbs_seq="AAGGGAGAAAT",
            cds_seq="ATGAACCGCACCAACATCGTCACCCGCGCCCTGCTGGCCGAACTGGCCGGTGTGGCCCAGGGCCTGCTGGAACAGTTACGCCGCCTGCCCGACGGCTGGCTGCTGGTC",
            terminator_seq="CCAGGCATCAAATAAAACGAAAGGCTCAGTCGAAAGACTGGGCCTTTCGTTTTATCTGTTGTTTGTCGGTGAACGCTCTC",
        ),
        RepressorParam(
            name="QacR",
            y_min=0.018,
            y_max=3.60,
            k_threshold=0.15,
            hill_coefficient=2.20,
            promoter_seq="TTTTCTATATTGACATTTTCTATATAATGAGCAC",
            rbs_seq="AAGGAGGTGTT",
            cds_seq="ATGAACCTGAAAGAAATCATCGACAGCGCCTTCGAACTGCTGAACGAAATCGGCATCCAGGGCCTGACCACCCGCAAGCTGGCCCAGAAGCTGGGCGTGGAACAGCCG",
            terminator_seq="CCAGGCATCAAATAAAACGAAAGGCTCAGTCGAAAGACTGGGCCTTTCGTTTTATCTGTTGTTTGTCGGTGAACGCTCTC",
        ),
        RepressorParam(
            name="BM3R1",
            y_min=0.010,
            y_max=5.00,
            k_threshold=0.09,
            hill_coefficient=3.50,
            promoter_seq="TGATGACAGTGACACATGATGACAGTGATAATGAGCAC",
            rbs_seq="AAGTAGGTGAA",
            cds_seq="ATGAACCGTCTGAACCTGCTGCGTGACGCCCTGCTGGCCGACCTGGCAGGTCGTGAACAGGCCCTGCTGGACGCGCTGCGCCGCCTGCCGGATGGCTGGCTGCTGGTC",
            terminator_seq="CCAGGCATCAAATAAAACGAAAGGCTCAGTCGAAAGACTGGGCCTTTCGTTTTATCTGTTGTTTGTCGGTGAACGCTCTC",
        ),
        RepressorParam(
            name="AmtR",
            y_min=0.022,
            y_max=4.50,
            k_threshold=0.20,
            hill_coefficient=2.60,
            promoter_seq="GAATGTGACAGTGACACGAATGTGACAGTGATAATGAGCAC",
            rbs_seq="AAGGAGACCAT",
            cds_seq="ATGACCCTGGCCCGCCTGGTCACCGACGCCCTGCAGGCCGAACTGGCCGGTGTGGCCCAGGGCCTGCTGGAACAGTTACGCCGCCTGCCCGACGGCTGGCTGCTGGTC",
            terminator_seq="CCAGGCATCAAATAAAACGAAAGGCTCAGTCGAAAGACTGGGCCTTTCGTTTTATCTGTTGTTTGTCGGTGAACGCTCTC",
        ),
    ]
    return {u.name: u for u in units}


def get_crosstalk_coefficient(repressor_a: str, repressor_b: str) -> float:
    """Return off-target non-cognate repression cross-coupling factor (0.0 to 1.0)."""
    if repressor_a == repressor_b:
        return 1.0
    # Symmetric non-cognate baseline interaction
    pair = tuple(sorted([repressor_a, repressor_b]))
    matrix = {
        ("LacI", "TetR"): 0.012,
        ("AmeRs", "PhlF"): 0.015,
        ("BetI", "QacR"): 0.018,
        ("AmtR", "BM3R1"): 0.010,
        ("BetI", "TetR"): 0.014,
        ("LacI", "PhlF"): 0.011,
    }
    return matrix.get(pair, 0.005)
