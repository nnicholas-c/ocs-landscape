"""Check the band-name part of matrix_build's self-check (code review: the
number check did not cover band names such as "C band").

Plain assert, no framework. Run with:
    .venv/bin/python -m pipeline.test_matrix_build
"""
from pipeline.matrix_build import bands, spec_cell


def demo():
    assert bands("C band (1530 to 1565 nm) and L band") == {"C", "L"}
    assert bands("over the C+L-band") == {"C", "L"}
    assert bands("in the C-band, S-band, and L-band") == {"C", "S", "L"}
    assert bands("C- and L-band") == {"C", "L"}
    assert bands("in the O-band") == {"O"}
    assert bands("C-Band") == {"C"}
    assert bands("S\u2010, C\u2010, and L\u2010bands") == {"S", "C", "L"}
    assert bands("O- to U-bands") == {"O", "U"}
    # Not band names: lowercase words, letters inside words, "TE-band"-like tokens.
    assert bands("a broad band, 1400-1700 nm, 256 FSR-free C-DCs, TE-band") == set()
    assert bands("C bandwidth, Ku-band, trl_band") == set()
    # The build rule, through spec_cell itself: a band in the value must be named in a quote.
    paper = lambda abstract: {"W1": {"abstract": abstract}}
    ok = spec_cell("lcos", "wavelength_range", {"value": "O band", "quotes": [["W1"]]},
                   paper("Works in the O-band."), {})
    assert ok["value"] == "O band"
    try:
        spec_cell("lcos", "wavelength_range", {"value": "1550 nm (C band)", "quotes": [["W1"]]},
                  paper("It switches at 1550 nm."), {})
        raise SystemExit("band check did not fire")
    except AssertionError as e:
        assert "band ['C']" in str(e), e
    print("test_matrix_build: ok")


if __name__ == "__main__":
    demo()
