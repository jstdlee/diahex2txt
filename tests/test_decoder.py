from pathlib import Path

import pytest

from diahex2txt.decoder import DiameterDecoder
from builder import avp, base, message, s, u32

DATA = Path(__file__).parent / "data"


def sample(name):
    return (DATA / f"{name}.hex").read_text().strip()


dec = DiameterDecoder().decode
HEADER_ONLY = "0100001480000110000000040000000000000000"


def test_header_only():
    r = dec(HEADER_ONLY)
    assert "Diameter Header:" in r
    assert "Code:         272 - CCR" in r
    assert "App ID:       4 - " in r
    assert "Version:      1" in r
    assert "header-only" in r
    assert "No AVPs found" not in r


def test_invalid_hex():
    assert "Error: Invalid hex string." in dec("zzzz")


def test_odd_length_rejected():
    assert dec("010").startswith("Error")


def test_empty():
    assert "Error: Empty input provided" in dec("")
    assert "Error: Empty input provided" in dec("  \n\t ")


@pytest.mark.parametrize("wrap", [
    lambda h: "0x" + h,
    lambda h: "0X" + h,
    lambda h: " ".join(h[i:i + 8] for i in range(0, len(h), 8)),
    lambda h: "\n".join(h[i:i + 16] for i in range(0, len(h), 16)) + "\r\n",
    lambda h: "\t" + h + "\t",
])
def test_input_formats(wrap):
    h = sample("gy_ccr")
    assert dec(wrap(h)) == dec(h)


def test_truncated_message():
    r = dec(HEADER_ONLY[:30])
    assert r.startswith("Error decoding") and "truncated" in r


def test_message_length_exceeds_data():
    h = sample("gy_ccr")
    assert "truncated message" in dec(h[:-8])


def test_bad_header_length():
    assert "invalid message length" in dec("01000004" + HEADER_ONLY[8:])


def test_bad_avp_length_warns_but_keeps_header():
    good = avp(263, b"abcd")
    bad = bytearray(avp(264, b"xyz"))
    bad[5:8] = (200).to_bytes(3, "big")
    r = dec(message(272, 4, [good, bytes(bad)]).hex())
    assert "Session-Id (Code: 263): abcd" in r
    assert "Warning" in r and "exceeds" in r


def test_avp_length_below_header():
    bad = bytearray(avp(264, b"xyz"))
    bad[5:8] = (3).to_bytes(3, "big")
    assert "invalid AVP length" in dec(message(272, 4, [bytes(bad)]).hex())


def test_multiple_messages():
    a = sample("gy_ccr")
    b = sample("s6a_ulr")
    r = dec(a + b)
    assert "=== Message 1 ===" in r and "=== Message 2 ===" in r
    assert "CCR" in r and "ULR" in r


def test_grouped_recursion():
    r = dec(sample("gy_ccr"))
    assert "      CC-Total-Octets (Code: 421): 104857600" in r
    assert "    Requested-Service-Unit (Code: 437)" in r


def test_deep_nesting_is_bounded():
    data = avp(1, b"x")
    for _ in range(40):
        data = avp(456, data)
    assert "nesting too deep" in dec(message(272, 4, [data]).hex())


def test_vendor_avp_uses_vendor_dictionary_and_shows_other_vendor_id():
    r = dec(message(272, 4, [u32(1032, 1004, 10415), u32(1032, 5, 99999)]).hex())
    assert "RAT-Type (Code: 1032): 1004" in r  # 3GPP id hidden
    assert "Unknown-Vendor-Specific-AVP (Code: 1032, Vendor-ID: 99999): 0x00000005" in r


def test_vendor_code_does_not_collide_with_base_code():
    # Code 1 is User-Name in base; vendor 99999 code 1 must not be named that
    r = dec(message(272, 4, [u32(1, 7, 99999)]).hex())
    assert "User-Name" not in r


def test_padding_between_avps():
    r = dec(message(272, 4, [s(263, "abcde"), s(264, "h")]).hex())
    assert "Session-Id (Code: 263): abcde" in r and "Origin-Host (Code: 264): h" in r


@pytest.mark.parametrize("name,needle", [
    ("gy_ccr", "CCR"), ("gy_cca", "CCA"), ("gx_ccr", "Gx"), ("gx_cca", "Charging-Rule-Name"),
    ("s6a_ulr", "ULR (Update-Location-Request)"), ("s6a_ula", "ULA (Update-Location-Answer)"),
    ("cx_uar", "UAR (User-Authorization-Request)"), ("swx_mar", "MAR (Multimedia-Auth-Request)"),
])
def test_interface_samples(name, needle):
    r = dec(sample(name))
    assert not r.startswith("Error")
    assert needle in r
    assert "Session-Id (Code: 263): sess;1" in r
    assert "Warning" not in r
    assert "Unknown-AVP" not in r


def test_same_code_differs_per_application():
    assert "SAR" in dec(message(300, 16777265, base()).hex())  # SWx
    assert "UAR" in dec(message(300, 16777216, base()).hex())  # Cx
