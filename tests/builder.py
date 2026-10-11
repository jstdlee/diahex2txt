"""Tiny independent Diameter encoder used to build test vectors."""
import struct


def avp(code, data, vendor=0, mandatory=True):
    flags = (0x80 if vendor else 0) | (0x40 if mandatory else 0)
    hdr = 12 if vendor else 8
    length = hdr + len(data)
    out = struct.pack(">I", code) + bytes([flags]) + length.to_bytes(3, "big")
    if vendor:
        out += struct.pack(">I", vendor)
    out += data + b"\0" * (-length % 4)
    return out


def u32(code, v, vendor=0):
    return avp(code, struct.pack(">I", v), vendor)


def s(code, text, vendor=0):
    return avp(code, text.encode(), vendor)


def grouped(code, *children, vendor=0):
    return avp(code, b"".join(children), vendor)


def message(code, app_id, avps, request=True, hbh=0x11223344, e2e=0x55667788):
    body = b"".join(avps)
    length = 20 + len(body)
    flags = 0xC0 if request else 0x40
    return (b"\x01" + length.to_bytes(3, "big") + bytes([flags]) + code.to_bytes(3, "big")
            + struct.pack(">III", app_id, hbh, e2e) + body)


def base(sid="sess;1", host="a.example.com", realm="example.com"):
    return [s(263, sid), s(264, host), s(296, realm)]
