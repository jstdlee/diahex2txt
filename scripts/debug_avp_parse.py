#!/usr/bin/env python
"""Debug AVP parsing"""
import binascii
from diameter.message import Message
from diameter.message.packer import Unpacker
from diameter.message.avp import Avp

hex_str = "010004704000011001000016a02cd02ccce2aeb4000001074000002a737472696e673b3439303b3032323b494d53493939393939313233343536373831300000000001024000000c01000016000001084000001b74766d2d76706372662e6d61676d612e636f6d0000000128400000116d61676d612e636f6d0000000000010c4000000c000007d1000001a04000000c000000010000019f4000000c00000000000001160000000c608fad23"

data = binascii.unhexlify(hex_str)
avp_data = data[20:]  # Skip header

print(f"Total data: {len(data)} bytes")
print(f"AVP data: {len(avp_data)} bytes")

unpacker = Unpacker(avp_data)
avp_count = 0

try:
    while not unpacker.done():
        print(f"\nParsing AVP #{avp_count}, position: {unpacker.get_position()}")
        try:
            avp = Avp.from_unpacker(unpacker)
            print(f"  Success: code={avp.code}, vendor={avp.vendor_id}")
            avp_count += 1
        except Exception as e:
            print(f"  Error: {e}")
            break
    print(f"\nTotal AVPs parsed: {avp_count}")
    print(f"Final position: {unpacker.get_position()}/{len(avp_data)}")
except Exception as e:
    print(f"Outer exception: {e}")
    import traceback
    traceback.print_exc()
