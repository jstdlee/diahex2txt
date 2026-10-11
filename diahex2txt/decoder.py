import binascii
import re
import struct
from datetime import datetime, timedelta, timezone
from ipaddress import ip_address
from typing import List, Optional, Tuple
from diameter.message.avp.dictionary import AVP_DICTIONARY, AVP_VENDOR_DICTIONARY

# Command codes. A request and its answer share one code (RFC 6733 section 3);
# the R flag in the header tells them apart.
# code -> (request abbreviation, answer abbreviation, base name)
BASE_COMMAND_CODES = {
    257: ("CER", "CEA", "Capabilities-Exchange"),
    258: ("RAR", "RAA", "Re-Auth"),
    265: ("AAR", "AAA", "AA"),
    268: ("DER", "DEA", "Diameter-EAP"),
    271: ("ACR", "ACA", "Accounting"),
    272: ("CCR", "CCA", "Credit-Control"),
    274: ("ASR", "ASA", "Abort-Session"),
    275: ("STR", "STA", "Session-Termination"),
    280: ("DWR", "DWA", "Device-Watchdog"),
    282: ("DPR", "DPA", "Disconnect-Peer"),
}

# Commands that depend on the application (same code, different meaning).
APP_COMMAND_CODES = {
    # S6a/S6d (TS 29.272)
    16777251: {
        316: ("ULR", "ULA", "Update-Location"),
        317: ("CLR", "CLA", "Cancel-Location"),
        318: ("AIR", "AIA", "Authentication-Information"),
        319: ("IDR", "IDA", "Insert-Subscriber-Data"),
        320: ("DSR", "DSA", "Delete-Subscriber-Data"),
        321: ("PUR", "PUA", "Purge-UE"),
        322: ("RSR", "RSA", "Reset"),
        323: ("NR", "NA", "Notify"),
    },
    # Cx/Dx (TS 29.229)
    16777216: {
        300: ("UAR", "UAA", "User-Authorization"),
        301: ("SAR", "SAA", "Server-Assignment"),
        302: ("LIR", "LIA", "Location-Info"),
        303: ("MAR", "MAA", "Multimedia-Auth"),
        304: ("RTR", "RTA", "Registration-Termination"),
        305: ("PPR", "PPA", "Push-Profile"),
    },
    # SWx (TS 29.273)
    16777265: {
        301: ("SAR", "SAA", "Server-Assignment"),
        303: ("MAR", "MAA", "Multimedia-Auth"),
        304: ("RTR", "RTA", "Registration-Termination"),
        305: ("PPR", "PPA", "Push-Profile"),
    },
    # Sh (TS 29.329)
    16777217: {
        306: ("UDR", "UDA", "User-Data"),
        307: ("PUR", "PUA", "Profile-Update"),
        308: ("SNR", "SNA", "Subscribe-Notifications"),
        309: ("PNR", "PNA", "Push-Notification"),
    },
    # S13/S13' (TS 29.272)
    16777252: {
        324: ("ECR", "ECA", "ME-Identity-Check"),
    },
}

# Application ID descriptions (IANA Diameter Application IDs)
APPLICATION_IDS = {
    # Base Diameter Applications
    0: "Diameter Common Messages",
    1: "NASREQ",
    2: "Mobile IPv4",
    3: "Diameter Base Accounting",
    4: "Diameter Credit Control (Gy/Ro)",
    5: "EAP",
    6: "SIP",

    # 3GPP Interfaces
    16777216: "Cx/Dx (3GPP IMS Subscription)",
    16777217: "Sh (3GPP AS-HSS)",
    16777219: "Wx (3GPP WLAN-AAA/HSS)",
    16777222: "Gq (3GPP Policy Control)",
    16777223: "Gmb (3GPP GGSN-BM-SC)",
    16777229: "Rx Release 6 (3GPP AF-PCRF)",
    16777230: "Pr (3GPP Presence)",
    16777236: "Rx (3GPP AF-PCRF)",
    16777238: "Gx (3GPP Policy Control)",
    16777250: "STa (3GPP Trusted WLAN Access)",
    16777251: "S6a/S6d (3GPP Mobility Management)",
    16777252: "S13/S13' (3GPP ME Identity Check)",
    16777255: "SLg (3GPP Location Services)",
    16777264: "SWm (3GPP ePDG-AAA)",
    16777265: "SWx (3GPP WLAN Authentication)",
    16777266: "Gxx (3GPP Gateway Control)",
    16777267: "S9 (3GPP Roaming Policy)",
    16777272: "S6b (3GPP PDN GW-3GPP AAA)",
    16777291: "SLh (3GPP Location Services)",
    16777302: "Sy (3GPP Policy Counters)",
    16777303: "Sd (3GPP TDF)",
    16777308: "S7a (3GPP Policy Control)",
    16777310: "S6m (3GPP MTC)",
    16777312: "S6c (3GPP SMS)",
    16777313: "SGd/Gdd (3GPP SGSN/GGSN)",
    16777318: "S15 (3GPP Congestion Management)",
    16777345: "S6t (3GPP HSS-SCEF)",
    16777346: "T6a/T6b (3GPP SCEF-MME/SGSN)",
}

# 3GPP Vendor ID (hidden in output for cleaner display)
VENDOR_3GPP = 10415

HEADER_LEN = 20
MAX_DEPTH = 16
_NTP_EPOCH = datetime(1900, 1, 1, tzinfo=timezone.utc)


def command_name(app_id: int, code: int, request: bool = True) -> str:
    entry = APP_COMMAND_CODES.get(app_id, {}).get(code) or BASE_COMMAND_CODES.get(code)
    if not entry:
        return "Unknown"
    req, ans, base = entry
    return f"{req} ({base}-Request)" if request else f"{ans} ({base}-Answer)"


class _Avp:
    """Minimal parsed AVP: header fields plus raw payload."""

    def __init__(self, code, flags, vendor_id, data):
        self.code, self.flags, self.vendor_id, self.data = code, flags, vendor_id, data


class DiameterDecoder:
    def decode(self, hex_input: str) -> str:
        """Decode one or more concatenated hex-encoded Diameter messages."""
        # Strip a 0x prefix from the input and from each whitespace-separated chunk
        chunks = [re.sub(r"^0[xX]", "", c) for c in (hex_input or "").split()]
        cleaned = "".join(chunks)
        if not cleaned:
            return "Error: Empty input provided."
        if len(cleaned) % 2 != 0:
            return "Error: Invalid hex string (odd number of digits)."
        try:
            data = binascii.unhexlify(cleaned)
        except (binascii.Error, ValueError):
            return "Error: Invalid hex string."

        outputs = []
        pos = 0
        while pos < len(data):
            rest = data[pos:]
            if len(rest) < HEADER_LEN:
                outputs.append(
                    f"Error decoding Diameter message: truncated header ({len(rest)} of {HEADER_LEN} bytes)."
                )
                break
            length = int.from_bytes(rest[1:4], "big")
            if length < HEADER_LEN:
                outputs.append(f"Error decoding Diameter message: invalid message length {length}.")
                break
            if length > len(rest):
                outputs.append(
                    f"Error decoding Diameter message: truncated message "
                    f"(header says {length} bytes, got {len(rest)})."
                )
                break
            outputs.append(self._decode_message(rest[:length]))
            pos += length
        if len(outputs) > 1:
            outputs = [f"=== Message {i} ===\n{o}" for i, o in enumerate(outputs, 1)]
        return "\n\n".join(outputs)

    def _decode_message(self, msg: bytes) -> str:
        version = msg[0]
        length = int.from_bytes(msg[1:4], "big")
        flags = msg[4]
        code = int.from_bytes(msg[5:8], "big")
        app_id, hbh, e2e = struct.unpack(">III", msg[8:20])

        flag_names = []
        if flags & 0x80: flag_names.append("Request")
        if flags & 0x40: flag_names.append("Proxiable")
        if flags & 0x20: flag_names.append("Error")
        if flags & 0x10: flag_names.append("Retransmitted")
        flags_str = ", ".join(flag_names) if flag_names else "None"

        out = [
            "Diameter Header:",
            f"  Version:      {version}",
            f"  Length:       {length}",
            f"  Flags:        {flags:#04x} ({flags_str})",
            f"  Code:         {code} - {command_name(app_id, code, bool(flags & 0x80))}",
            f"  App ID:       {app_id} - {APPLICATION_IDS.get(app_id, 'Unknown')}",
            f"  Hop-by-Hop:   {hbh:#010x}",
            f"  End-to-End:   {e2e:#010x}",
            "",
            "AVPs:",
        ]
        if len(msg) == HEADER_LEN:
            out.append("  (none - header-only message)")
            return "\n".join(out)
        lines, err = self._format_avps(msg[HEADER_LEN:], 0)
        out.extend(lines)
        if err:
            out.append(f"  (Warning: {err})")
        return "\n".join(out)

    # -- AVP parsing -------------------------------------------------------
    @staticmethod
    def _parse_avps(buf: bytes) -> Tuple[List[_Avp], Optional[str]]:
        """Parse AVPs from raw bytes. Returns (avps, error); stops at the first bad AVP."""
        avps, pos = [], 0
        while pos < len(buf):
            if len(buf) - pos < 8:
                return avps, f"truncated AVP header at offset {pos}"
            code = int.from_bytes(buf[pos:pos + 4], "big")
            flags = buf[pos + 4]
            length = int.from_bytes(buf[pos + 5:pos + 8], "big")
            hdr = 12 if flags & 0x80 else 8
            if length < hdr:
                return avps, f"invalid AVP length {length} for AVP code {code}"
            if pos + length > len(buf):
                return avps, f"AVP code {code} length {length} exceeds remaining {len(buf) - pos} bytes"
            vendor = int.from_bytes(buf[pos + 8:pos + 12], "big") if flags & 0x80 else 0
            avps.append(_Avp(code, flags, vendor, buf[pos + hdr:pos + length]))
            pos += (length + 3) & ~3  # AVPs are padded to 4 bytes
        return avps, None

    def _format_avps(self, buf: bytes, level: int) -> Tuple[List[str], Optional[str]]:
        avps, err = self._parse_avps(buf)
        lines: List[str] = []
        for avp in avps:
            lines.extend(self._format_avp(avp, level))
        return lines, err

    def _lookup(self, avp: _Avp) -> Optional[dict]:
        if avp.vendor_id:
            return AVP_VENDOR_DICTIONARY.get(avp.vendor_id, {}).get(avp.code)
        return AVP_DICTIONARY.get(avp.code)

    def _get_avp_name(self, avp: _Avp) -> str:
        d = self._lookup(avp)
        if d:
            return d.get("name", "Unknown")
        return "Unknown-Vendor-Specific-AVP" if avp.vendor_id else "Unknown-AVP"

    @staticmethod
    def _hex(b: bytes) -> str:
        return "0x" + binascii.hexlify(b).decode()

    def _format_value(self, avp: _Avp, type_name: str) -> str:
        b = avp.data
        try:
            if type_name in ("AvpUnsigned32", "AvpUnsigned64", "AvpInteger32", "AvpInteger64", "AvpEnumerated"):
                width = 8 if type_name.endswith("64") else 4
                if len(b) == width:
                    return str(int.from_bytes(b, "big", signed=type_name.startswith("AvpInteger") or type_name == "AvpEnumerated"))
            elif type_name == "AvpUtf8String":
                return b.decode("utf-8")
            elif type_name == "AvpAddress":
                fam = int.from_bytes(b[:2], "big")
                if fam == 1 and len(b) == 6:
                    return str(ip_address(b[2:]))
                if fam == 2 and len(b) == 18:
                    return str(ip_address(b[2:]))
            elif type_name == "AvpTime" and len(b) == 4:
                return str(_NTP_EPOCH + timedelta(seconds=int.from_bytes(b, "big")))
            elif type_name == "AvpFloat32" and len(b) == 4:
                return str(struct.unpack(">f", b)[0])
            elif type_name == "AvpFloat64" and len(b) == 8:
                return str(struct.unpack(">d", b)[0])
        except (ValueError, UnicodeDecodeError, OverflowError):
            pass
        # OctetString, or a value that did not fit its type
        if type_name == "AvpOctetString" and b:
            try:
                s = b.decode("utf-8")
                if s.isprintable():
                    return s
            except UnicodeDecodeError:
                pass
        return self._hex(b)

    def _format_avp(self, avp: _Avp, level: int) -> List[str]:
        indent = "  " * (level + 1)
        name = self._get_avp_name(avp)
        vid = f", Vendor-ID: {avp.vendor_id}" if avp.vendor_id and avp.vendor_id != VENDOR_3GPP else ""
        head = f"{indent}{name} (Code: {avp.code}{vid})"
        d = self._lookup(avp)
        type_name = d["type"].__name__ if d and "type" in d else "AvpOctetString"
        if type_name == "AvpGrouped":
            if level >= MAX_DEPTH:
                return [head + ": (nesting too deep)"]
            lines = [head]
            sub, err = self._format_avps(avp.data, level + 1)
            lines.extend(sub)
            if err:
                lines.append(f"{indent}  (Warning: {err})")
            return lines
        return [f"{head}: {self._format_value(avp, type_name)}"]
