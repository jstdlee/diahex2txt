from diahex2txt.decoder import DiameterDecoder
from datetime import datetime

class FakeAvp:
    def __init__(self):
        self.some_date = datetime.now()

class FakeMsg:
    def __init__(self):
        self.header = type('Header', (), {
            'is_request': True, 'is_proxyable': False, 'is_error': False, 'is_retransmit': False,
            'version': 1, 'length': 20, 'command_flags': 0, 'command_code': 272,
            'application_id': 4, 'hop_by_hop_identifier': 123, 'end_to_end_identifier': 456
        })()
        # This will trigger the fallback path in decoder for attribute-based AVPs
        self.some_complex_object = FakeAvp()

def test_recursion_fix():
    decoder = DiameterDecoder()
    # We can't easily mock the internal state without parsing a real message or mocking heavily.
    # But we can call _format_attribute directly to test the fix.
    
    val = datetime(2023, 1, 1, 12, 0, 0)
    lines = decoder._format_attribute("TestDate", val, 0)
    print("Lines:", lines)
    assert lines[0] == "  TestDate: 2023-01-01 12:00:00"
    
    # Test valid complex object that contains a date
    complex_obj = FakeAvp()
    lines_complex = decoder._format_attribute("Complex", complex_obj, 0)
    print("Complex Lines:", lines_complex)
    # expected:
    #   Complex: FakeAvp
    #     some_date: <date string>
    assert "some_date" in lines_complex[1]

if __name__ == "__main__":
    test_recursion_fix()
