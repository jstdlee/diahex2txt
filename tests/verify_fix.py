from diahex2txt.decoder import DiameterDecoder
import sys

try:
    decoder = DiameterDecoder()
    hex_str = "0100001480000110000000040000000000000000"
    result = decoder.decode(hex_str)
    print("SUCCESS")
    print(result)
except Exception as e:
    print("FAILURE")
    print(e)
