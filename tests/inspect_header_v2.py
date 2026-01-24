from diameter.message import Message
import binascii
import sys

hex_str = "0100001480000110000000040000000000000000"
data = binascii.unhexlify(hex_str)

try:
    msg = Message.from_bytes(data)
    h = msg.header
    print(f"Header Type: {type(h)}")
    print("Header Dir:", dir(h))
    try:
        print("Header Vars:", vars(h))
    except:
        print("Header has no __dict__")
        
except Exception as e:
    print(f"Error: {e}")
