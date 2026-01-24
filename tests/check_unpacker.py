#!/usr/bin/env python
"""Check Unpacker API"""
from diameter.message.packer import Unpacker
import binascii

# Small test data
data = binascii.unhexlify("000001074000002a737472696e673b3439303b3032323b494d5349393939393931323334353637383130000000")

unpacker = Unpacker(data)
print(f"Unpacker type: {type(unpacker)}")
print(f"Unpacker attributes: {[a for a in dir(unpacker) if not a.startswith('_')]}")

# Try to use it
try:
    val = unpacker.unpack_uint32()
    print(f"Unpacked uint32: {val}")
except Exception as e:
    print(f"Error: {e}")
