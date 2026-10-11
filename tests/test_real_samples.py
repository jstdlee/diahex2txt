"""Regression tests on messages copied from public Diameter captures.

See the header of data/real_samples.hex for sources and licences.
"""
from pathlib import Path

import pytest

from diahex2txt.decoder import DiameterDecoder, command_name

FILE = Path(__file__).parent / "data" / "real_samples.hex"


def _load():
    items, expect = [], None
    for line in FILE.read_text().splitlines():
        if line.startswith("# expect: "):
            expect = line[len("# expect: "):]
        elif line and not line.startswith("#"):
            items.append((expect, line))
            expect = None
    return items


ITEMS = _load()


@pytest.mark.parametrize("expect,hex_str", ITEMS)
def test_real_message(expect, hex_str):
    r = DiameterDecoder().decode(hex_str)
    assert r.startswith("Diameter Header:")
    assert expect in r
    assert "Warning" not in r
    assert "Unknown" not in r.split("AVPs:")[0]


def test_real_samples_present():
    assert len(ITEMS) >= 9


def test_framed_ip_address_shows_ipv4():
    gx_ccr = [h for e, h in ITEMS if e and "272 - CCR" in e and "16777238" in DiameterDecoder().decode(h)]
    assert any("Framed-IP-Address (Code: 8): " in DiameterDecoder().decode(h) and
               "Framed-IP-Address (Code: 8): 0x" not in DiameterDecoder().decode(h) for h in gx_ccr)


@pytest.mark.parametrize("app,code,text", [
    (6, 283, "UAR (User-Authorization-Request)"),
    (6, 288, "PPR (Push-Profile-Request)"),
    (2, 260, "AMR (AA-Mobile-Node-Request)"),
    (2, 262, "HAR (Home-Agent-MIP-Request)"),
    (16777304, 8388633, "SLR (Ericsson-SL-Request)"),
    (16777302, 8388635, "SLR (Spending-Limit-Request)"),
    (16777302, 8388636, "SNR (Spending-Status-Notification-Request)"),
    (16777255, 8388620, "PLR (Provide-Location-Request)"),
    (16777291, 8388622, "RIR (LCS-Routing-Info-Request)"),
    (16777313, 8388645, "OFR (MO-Forward-Short-Message-Request)"),
    (16777312, 8388647, "SRR (Send-Routing-Info-for-SM-Request)"),
])
def test_newer_command_codes(app, code, text):
    assert command_name(app, code, True) == text
