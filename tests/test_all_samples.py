#!/usr/bin/env python
"""Test all samples from samples.txt"""
from diahex2txt.decoder import DiameterDecoder

decoder = DiameterDecoder()

with open("samples.txt", "r") as f:
    samples = [line.strip() for line in f if line.strip()]

for i, hex_str in enumerate(samples, 1):
    print(f"=== Sample {i} ===")
    result = decoder.decode(hex_str)
    
    # Count AVPs
    avp_lines = [line for line in result.split("\n") if "(Code:" in line]
    print(f"Decoded {len(avp_lines)} AVPs")
    
    # Show first few AVPs
    print("First 5 AVPs:")
    for line in avp_lines[:5]:
        print(f"  {line.strip()}")
    
    print()
