import binascii
from typing import List, Any, Union
from diameter.message import Message, Avp, AvpGrouped
from diameter.message.avp.dictionary import AVP_DICTIONARY, AVP_VENDOR_DICTIONARY

# Command Code descriptions - 3GPP LTE Diameter Interfaces
COMMAND_CODES = {
    # Base Diameter Protocol (RFC 6733)
    257: "CER (Capabilities-Exchange-Request)",
    258: "CEA (Capabilities-Exchange-Answer)",
    265: "AAR (AA-Request)",
    266: "AAA (AA-Answer)",
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
    
    # S6a/S6d Interface (EPS Mobility Management)
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
    326: "RER (Reset-Request)",
    327: "REA (Reset-Answer)",
    328: "NOR (Notify-Request)",
    329: "NOA (Notify-Answer)",
    
    # S13/S13' Interface (ME Identity Check)
    324: "ECR (ECR-Request)",  # Note: Reused code 324
    325: "ECA (ECA-Answer)",   # Note: Reused code 325
    
    # SWx Interface (WLAN Authentication)
    303: "MAR (Multimedia-Auth-Request)",
    304: "MAA (Multimedia-Auth-Answer)",
    301: "SAR (Server-Assignment-Request)",
    302: "SAA (Server-Assignment-Answer)",
    287: "RTR (Registration-Termination-Request)",
    288: "RTA (Registration-Termination-Answer)",
    305: "PPR (Push-Profile-Request)",
    306: "PPA (Push-Profile-Answer)",
    
    # Cx/Dx Interface (IMS Subscription)
    300: "UAR (User-Authorization-Request)",
    301: "UAA (User-Authorization-Answer)",
    # 301-306 shared with SWx above
    
    # Sh Interface (Application Server - HSS)
    306: "UDR (User-Data-Request)",
    307: "UDA (User-Data-Answer)",
    308: "PUR (Profile-Update-Request)",
    309: "PUA (Profile-Update-Answer)",
    310: "SNR (Subscribe-Notifications-Request)",
    311: "SNA (Subscribe-Notifications-Answer)",
    312: "PNR (Push-Notification-Request)",
    313: "PNA (Push-Notification-Answer)",
    
    # Sy Interface (Policy Counter Status)
    8388635: "SLR (Spending-Limit-Request)",
    8388636: "SLA (Spending-Limit-Answer)",
    8388637: "SNR (Spending-Status-Notification-Request)",
    8388638: "SNA (Spending-Status-Notification-Answer)",
    
    # Gx Interface (Policy Control - already covered by CCR/CCA)
    8388620: "RAR (Re-Auth-Request)",
    8388621: "RAA (Re-Auth-Answer)",
    
    # Rx Interface (Application - PCRF)
    # Uses AAR/AAA (265/266), STR/STA (291/292), ASR/ASA (274/275)
    292: "STA (Session-Termination-Answer)",
    
    # S9 Interface (Roaming Policy Control)
    # Uses CCR/CCA (272/273), RAR/RAA (8388620/8388621)
    
    # Sd Interface (TDF - PCRF)
    # Uses CCR/CCA, RAR/RAA
    
    # S6c Interface (SMS over IP)
    8388647: "SRR (Send-Routing-Info-Request)",
    8388648: "SRA (Send-Routing-Info-Answer)",
    8388645: "ALR (Alert-Service-Centre-Request)",
    8388646: "ALA (Alert-Service-Centre-Answer)",
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
    16777223: "Rf (3GPP Offline Charging)",
    16777229: "SWm (3GPP WLAN-AAA)",
    16777238: "Gx (3GPP Policy Control)",
    16777250: "SWx (3GPP WLAN Authentication)",
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
    16777231: "STa (3GPP Trusted WLAN Access)",
    16777250: "SWx (3GPP AAA-HSS)",
    16777265: "Gmb (3GPP GGSN-BM-SC)",
    16777281: "Mm10 (3GPP IMS Service Control)",
    16777308: "S15 (3GPP CS-PS Coordination)",
}

# 3GPP Vendor ID (simplified display)
VENDOR_3GPP = 10415

class DiameterDecoder:
    def decode(self, hex_input: str) -> str:
        # Clean input
        cleaned_hex = hex_input.strip().replace(" ", "").replace("\n", "").replace("0x", "")
        
        # Validation
        if not cleaned_hex:
            return "Error: Empty input provided."
        try:
            # Ensure even length
            if len(cleaned_hex) % 2 != 0:
                 cleaned_hex = "0" + cleaned_hex
            data = binascii.unhexlify(cleaned_hex)
        except binascii.Error:
            return "Error: Invalid hex string."
        except Exception as e:
            return f"Error converting hex to bytes: {e}"

        try:
            # Parse message
            # Message.from_bytes(data) returns a Message instance
            msg = Message.from_bytes(data)
        except Exception as e:
            return f"Error decoding Diameter message: {e}\n(Ensure the hex includes the full Diameter header and payload)"

        output = []
        
        # --- Header ---
        h = msg.header
        output.append("Diameter Header:")
        
        # Flags
        flags = []
        if h.is_request: flags.append("Request")
        if h.is_proxyable: flags.append("Proxiable")
        if h.is_error: flags.append("Error")
        if h.is_retransmit: flags.append("Retransmitted")
        flags_str = ", ".join(flags) if flags else "None"
        
        # Command Code with description
        cmd_desc = COMMAND_CODES.get(h.command_code, "Unknown")
        
        # Application ID with description
        app_desc = APPLICATION_IDS.get(h.application_id, "Unknown")
        
        output.append(f"  Version:      {h.version}")
        output.append(f"  Length:       {h.length}")
        output.append(f"  Flags:        {h.command_flags:#02x} ({flags_str})")
        output.append(f"  Code:         {h.command_code} - {cmd_desc}")
        output.append(f"  App ID:       {h.application_id} - {app_desc}")
        output.append(f"  Hop-by-Hop:   {h.hop_by_hop_identifier:#010x}")
        output.append(f"  End-to-End:   {h.end_to_end_identifier:#010x}")
        output.append("")
        
        output.append("AVPs:")
        
        # --- AVPs ---
        # Attempt to retrieve AVPs from the message.
        # python-diameter usually stores them in _avps list in order of appearance
        avp_list = []
        if hasattr(msg, '_avps') and isinstance(msg._avps, list) and len(msg._avps) > 0:
             avp_list = msg._avps
        elif not avp_list:
             # For typed messages where AVPs are consumed, manually parse from bytes
             # This preserves the original wire order
             try:
                 avp_list = self._parse_avps_from_bytes(data[20:])  # Skip 20-byte header
             except Exception as e:
                 output.append(f"  (Warning: Could not parse raw AVPs: {e})")
                 avp_list = []

        if avp_list:
            for avp in avp_list:
                output.extend(self._format_avp(avp, level=0))
        else:
            output.append("  No AVPs found or unable to extract.")

        return "\n".join(output)
    
    def _parse_avps_from_bytes(self, avp_data: bytes) -> List[Avp]:
        """Manually parse AVPs from raw bytes to preserve order."""
        from diameter.message.packer import Unpacker
        
        avps = []
        unpacker = Unpacker(avp_data)
        
        while unpacker.get_position() < len(avp_data):
            try:
                avp = Avp.from_unpacker(unpacker)
                avps.append(avp)
            except Exception:
                # Stop on error (end of data or malformed AVP)
                break
                
        return avps

    def _format_attribute(self, name: str, value: Any, level: int) -> List[str]:
        # Formatter for attribute-based AVPs
        indent = "  " * (level + 1)
        lines = []
        
        # Handle simple types first
        if value is None:
             lines.append(f"{indent}{name}: None")
             return lines
             
        from datetime import datetime, date, time
        if isinstance(value, (str, int, float, bool, datetime, date, time)):
             lines.append(f"{indent}{name}: {value}")
             return lines
             
        if isinstance(value, bytes):
             try:
                 val_str = value.decode('utf-8')
                 # Check if it looks like a meaningful string (optional, but good for safety)
                 if not val_str.isprintable(): 
                      raise ValueError
             except:
                 val_str = f"0x{binascii.hexlify(value).decode()}"
             lines.append(f"{indent}{name}: {val_str}")
             return lines

        # Handle List
        if isinstance(value, list):
             lines.append(f"{indent}{name}: (List)")
             for item in value:
                  lines.extend(self._format_attribute("Item", item, level + 1))
             return lines
        
        # Handle Complex Objects
        # We assume anything else might be a container object (like MultipleServicesCreditControl)
        # We want to print its class name and then its attributes
        type_name = type(value).__name__
        lines.append(f"{indent}{name}: {type_name}")
        
        # Extract meaningful attributes
        # Filter out privates, callables, and metadata like 'avp', 'header'
        try:
            # vars() works if __dict__ exists
            attrs = [k for k in vars(value) if not k.startswith("_")]
        except TypeError:
            # fallback for objects without __dict__ (e.g. slots, though unusual here)
            attrs = [k for k in dir(value) if not k.startswith("_") and not callable(getattr(value, k))]
            
        # Specific exclusions if needed
        attrs = [k for k in attrs if k not in ("header", "avp_code", "avp_vendor", "is_mandatory", "is_private")]
        
        if not attrs:
             # Fallback to str() if no attrs found
             pass # Already printed Name: TypeName, maybe append str? 
             # actually let's just leave it as TypeName or try str(value) if we prefer
             # but user wants expansion. If empty, maybe it's effectively empty.
        else:
             for attr_name in attrs:
                 val = getattr(value, attr_name)
                 lines.extend(self._format_attribute(attr_name, val, level + 1))
                 
        return lines

    def _format_avp(self, avp: Avp, level: int) -> List[str]:
        lines = []
        indent = "  " * (level + 1)
        
        # Get Name
        name = self._get_avp_name(avp)
        
        is_grouped = isinstance(avp, AvpGrouped)
        
        # Determine value display
        if is_grouped:
            # Header line for grouped
            # Name (Code):
            # Hide vendor ID 10415 (3GPP) for cleaner output
            vid_str = ""
            if avp.vendor_id and avp.vendor_id != VENDOR_3GPP:
                vid_str = f", Vendor-ID: {avp.vendor_id}"
            lines.append(f"{indent}{name} (Code: {avp.code}{vid_str})")
            
            # Recurse
            # If standard grouped logic didn't populate _avps, look at .value
            if hasattr(avp, '_avps') and isinstance(avp._avps, list):
                  for sub_avp in avp._avps:
                       lines.extend(self._format_avp(sub_avp, level + 1))
            elif isinstance(avp.value, list):
                  for sub in avp.value:
                      if isinstance(sub, Avp):
                          lines.extend(self._format_avp(sub, level + 1))
                      else:
                          # Unexpected content in grouped AVP
                          lines.extend(self._format_attribute("Value", sub, level + 1))
        else:
            # Basic value
            val = avp.value
            val_str = ""
            if isinstance(val, bytes):
                try:
                    # Try utf-8
                    val_str = val.decode("utf-8")
                    if not val_str.isprintable():
                         val_str = f"0x{binascii.hexlify(val).decode()}"
                except:
                    val_str = f"0x{binascii.hexlify(val).decode()}"
            else:
                val_str = str(val)

            # Hide vendor ID 10415 (3GPP) for cleaner output
            vid_str = ""
            if avp.vendor_id and avp.vendor_id != VENDOR_3GPP:
                vid_str = f", Vendor-ID: {avp.vendor_id}"
            header_line = f"{indent}{name} (Code: {avp.code}{vid_str}): {val_str}"
            lines.append(header_line)
        
        return lines

    def _get_avp_name(self, avp: Avp) -> str:
        # Check standard dictionary
        # dictionary[code] -> definition
        if avp.code in AVP_DICTIONARY:
             # definition is a dict
             return AVP_DICTIONARY[avp.code].get('name', 'Unknown')
        
        # Check vendor
        if avp.vendor_id and avp.vendor_id in AVP_VENDOR_DICTIONARY:
             v_dict = AVP_VENDOR_DICTIONARY[avp.vendor_id]
             if avp.code in v_dict:
                 return v_dict[avp.code].get('name', 'Unknown-Vendor-Specific')
                 
        return "Unknown-AVP"
