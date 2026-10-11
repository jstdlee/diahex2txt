import binascii
import re
import struct
from datetime import datetime, timedelta, timezone
from ipaddress import ip_address
from typing import List, Optional, Tuple
from diameter.message.avp.dictionary import AVP_DICTIONARY, AVP_VENDOR_DICTIONARY

# Command code names. Base commands apply to every application.
BASE_COMMAND_CODES = {
    257: "CER (Capabilities-Exchange-Request)",
    258: "CEA (Capabilities-Exchange-Answer)",
    265: "AAR (AA-Request)",
    266: "AAA (AA-Answer)",
    268: "DER (Diameter-EAP-Request)",
    271: "ACR (Accounting-Request)",
    272: "CCR (Credit-Control-Request)",
    273: "CCA (Credit-Control-Answer)",
    274: "ASR (Abort-Session-Request)",
    275: "ASA (Abort-Session-Answer)",
    280: "DWR (Device-Watchdog-Request)",
    281: "DWA (Device-Watchdog-Answer)",
    282: "DPR (Disconnect-Peer-Request)",
    283: "DPA (Disconnect-Peer-Answer)",
    291: "STR (Session-Termination-Request)",
    292: "STA (Session-Termination-Answer)",
    8388620: "RAR (Re-Auth-Request)",
    8388621: "RAA (Re-Auth-Answer)",
}

# Command names that depend on the application (same code, different meaning).
APP_COMMAND_CODES = {
    # S6a/S6d
    16777251: {
        316: "ULR (Update-Location-Request)",
        317: "ULA (Update-Location-Answer)",
        318: "AIR (Authentication-Information-Request)",
        319: "AIA (Authentication-Information-Answer)",
        320: "IDR (Insert-Subscriber-Data-Request)",
        321: "IDA (Insert-Subscriber-Data-Answer)",
        322: "DSR (Delete-Subscriber-Data-Request)",
        323: "DSA (Delete-Subscriber-Data-Answer)",
        324: "PUR (Purge-UE-Request)",
        325: "PUA (Purge-UE-Answer)",
        326: "RSR (Reset-Request)",
        327: "RSA (Reset-Answer)",
        328: "NR (Notify-Request)",
        329: "NA (Notify-Answer)",
    },
    # Cx/Dx
    16777216: {
        300: "UAR (User-Authorization-Request)",
        301: "UAA (User-Authorization-Answer)",
        302: "SAR (Server-Assignment-Request)",
        303: "SAA (Server-Assignment-Answer)",
        304: "LIR (Location-Info-Request)",
        305: "LIA (Location-Info-Answer)",
        306: "MAR (Multimedia-Auth-Request)",
        307: "MAA (Multimedia-Auth-Answer)",
        308: "RTR (Registration-Termination-Request)",
        309: "RTA (Registration-Termination-Answer)",
        310: "PPR (Push-Profile-Request)",
        311: "PPA (Push-Profile-Answer)",
    },
    # SWx
    16777265: {
        300: "SAR (Server-Assignment-Request)",
        301: "SAA (Server-Assignment-Answer)",
        303: "MAR (Multimedia-Auth-Request)",
        304: "MAA (Multimedia-Auth-Answer)",
        305: "RTR (Registration-Termination-Request)",
        306: "RTA (Registration-Termination-Answer)",
        307: "PPR (Push-Profile-Request)",
        308: "PPA (Push-Profile-Answer)",
    },
    # Sh
    16777217: {
        306: "UDR (User-Data-Request)",
        307: "UDA (User-Data-Answer)",
        308: "PUR (Profile-Update-Request)",
        309: "PUA (Profile-Update-Answer)",
        310: "SNR (Subscribe-Notifications-Request)",
        311: "SNA (Subscribe-Notifications-Answer)",
        312: "PNR (Push-Notification-Request)",
        313: "PNA (Push-Notification-Answer)",
    },
    # S13
    16777252: {
        324: "ECR (ME-Identity-Check-Request)",
        325: "ECA (ME-Identity-Check-Answer)",
    },
}

# Application ID descriptions - 3GPP LTE Interfaces
APPLICATION_IDS = {
    # Base Diameter Applications
    0: "Diameter Common Messages",
    1: "NASREQ",
    2: "Mobile IPv4",
    3: "Diameter Base Accounting",
    4: "Diameter Credit Control (Gy/Gz)",
    5: "EAP",
    6: "SIP",
    
    # 3GPP Interfaces
    16777216: "Cx/Dx (3GPP IMS Subscription)",
    16777217: "Sh (3GPP AS-HSS)",
    16777222: "Ro (3GPP Online Charging)",
    16777229: "SWm (3GPP WLAN-AAA)",
    16777238: "Gx (3GPP Policy Control)",
    16777265: "SWx (3GPP WLAN Authentication)",
    16777251: "S6a/S6d (3GPP Mobility Management)",
    16777252: "S13/S13' (3GPP ME Identity Check)",
    16777261: "S6c (3GPP SMS)",
    16777264: "SGd/Gdd (3GPP SGSN/GGSN)",
    16777267: "S9 (3GPP Roaming Policy)",
    16777268: "S6b (3GPP PDN GW-3GPP AAA)",
    16777272: "SLg (3GPP Location Services)",
    16777291: "Sy (3GPP Policy Counters)",
    16777302: "Rx (3GPP AF-PCRF)",
    16777303: "Gxx (3GPP Trusted WLAN)",
    16777318: "S6m (3GPP MTC)",
    16777334: "T6a/T6b (3GPP SCEF)",
    16777335: "S6t (3GPP HSS-IWK-SCEF)",
    
    # Additional 3GPP Interfaces
    16777219: "Pr (3GPP Presence)",
    16777250: "STa (3GPP Trusted WLAN Access)",
    16777223: "Gmb (3GPP GGSN-BM-SC)",
    16777281: "Mm10 (3GPP IMS Service Control)",
    16777308: "S15 (3GPP CS-PS Coordination)",
}

# 3GPP Vendor ID (hidden in output for cleaner display)
VENDOR_3GPP = 10415

HEADER_LEN = 20
MAX_DEPTH = 16
_NTP_EPOCH = datetime(1900, 1, 1, tzinfo=timezone.utc)


def command_name(app_id: int, code: int) -> str:
    return APP_COMMAND_CODES.get(app_id, {}).get(code) or BASE_COMMAND_CODES.get(code, "Unknown")


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
            f"  Code:         {code} - {command_name(app_id, code)}",
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
