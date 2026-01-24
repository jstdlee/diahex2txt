from diameter.message import Message
import binascii

hex_str = "0100001480000110000000040000000000000000"
data = binascii.unhexlify(hex_str)

with open("debug_output.txt", "w") as f:
    try:
        msg = Message.from_bytes(data)
        f.write(f"Message Type: {type(msg)}\n")
        f.write(f"Dir: {dir(msg)}\n")
        f.write(f"Vars: {vars(msg)}\n")
        
        if hasattr(msg, 'avp'):
            f.write("Has 'avp' attribute\n")
        
        if hasattr(msg, '_avps'):
             f.write(f"_avps: {msg._avps}\n")

    except Exception as e:
        f.write(f"Error: {e}\n")
