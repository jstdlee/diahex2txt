from pathlib import Path

import pytest

from diahex2txt.decoder import DiameterDecoder

SAMPLES = Path(__file__).parent / "samples.txt"
LINES = [l.strip() for l in SAMPLES.read_text().splitlines() if l.strip() and not l.startswith("#")]


@pytest.mark.parametrize("hex_str", LINES)
def test_sample_decodes(hex_str):
    r = DiameterDecoder().decode(hex_str)
    assert r.startswith("Diameter Header:")
    assert "Warning" not in r
    assert len([l for l in r.splitlines() if "(Code:" in l]) >= 3


def test_all_samples_as_one_stream():
    r = DiameterDecoder().decode("".join(LINES))
    assert r.count("=== Message") == len(LINES)
