import pytest
from diahex2txt.decoder import DiameterDecoder

def test_decode_header_only():
    decoder = DiameterDecoder()
    # CCR header (Credit-Control-Request)
    # 01 (Ver) 000014 (Len=20) 80 (Req) 000110 (272) 00000004 (4) ...
    hex_str = "0100001480000110000000040000000000000000"
    result = decoder.decode(hex_str)
    assert "Diameter Header:" in result
    assert "Cmd Code:         272" in result
    assert "App ID:       4" in result
    assert "Version:      1" in result

def test_decode_invalid_hex():
    decoder = DiameterDecoder()
    result = decoder.decode("zzzz")
    assert "Error: Invalid hex characters" in result

def test_decode_empty():
    decoder = DiameterDecoder()
    result = decoder.decode("")
    assert "Error: Empty input provided" in result
