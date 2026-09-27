"""Check the band-name part of matrix_build's self-check (code review: the
number check did not cover band names such as "C band").

Plain assert, no framework. Run with:
    .venv/bin/python -m pipeline.test_matrix_build
"""
from pipeline.matrix_build import bands


def demo():
    assert bands("C band (1530 to 1565 nm) and L band") == {"C", "L"}
    assert bands("over the C+L-band") == {"C", "L"}
    assert bands("in the C-band, S-band, and L-band") == {"C", "S", "L"}
    assert bands("C- and L-band") == {"C", "L"}
    assert bands("in the O-band") == {"O"}
    # Not band names: lowercase words, letters inside words, "TE-band"-like tokens.
    assert bands("a broad band, 1400-1700 nm, 256 FSR-free C-DCs, TE-band") == set()
    # The build rule: value bands must be a subset of quote bands.
    assert bands("O band") - bands("45-nm optical bandwidth in the O-band") == set()
    assert bands("C band") - bands("operating at 1550 nm") == {"C"}
    print("test_matrix_build: ok")


if __name__ == "__main__":
    demo()
