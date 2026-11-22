"""Tests for orthogonal transcriptional repressor library and parameters."""

from biological_logic_compiler.library import (
    get_crosstalk_coefficient,
    get_default_repressor_library,
)


def test_repressor_library_contents():
    lib = get_default_repressor_library()
    assert len(lib) >= 8
    for rep in lib.values():
        assert rep.y_max > rep.y_min
        assert rep.k_threshold > 0.0
        assert rep.hill_coefficient >= 1.0
        assert len(rep.promoter_seq) > 10
        assert len(rep.cds_seq) > 10

def test_crosstalk_coefficients():
    assert get_crosstalk_coefficient("TetR", "TetR") == 1.0
    c_cross = get_crosstalk_coefficient("LacI", "TetR")
    assert 0.0 < c_cross < 0.05
    c_unknown = get_crosstalk_coefficient("UnknownA", "UnknownB")
    assert c_unknown <= 0.01
