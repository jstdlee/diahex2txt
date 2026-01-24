from diameter.message import Message
import binascii

hex_str = "0100001480000110000000040000000000000000"
data = binascii.unhexlify(hex_str)

try:
    msg = Message.from_bytes(data)
    h = msg.header
    print(f"Header type: {type(h)}")
    print(f"Header dir: {dir(h)}")
    print(f"Header flags: {h.flags}")
except Exception as e:
    print(f"Error: {e}")
