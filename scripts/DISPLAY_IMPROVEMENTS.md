# Decoder Improvements Summary

## Changes Made

### 1. Command Code and Application ID Descriptions
Added human-readable descriptions to the Diameter Header:

**Before:**
```
  Code:         272
  App ID:       16777238
```

**After:**
```
  Code:         272 - CCR (Credit-Control-Request)
  App ID:       16777238 - Gx (3GPP)
```

Supported command codes:
- 257-283: CER, CEA, AAR, AAA, CCR, CCA, ASR, ASA, DWR, DWA, DPR, DPA
- 316-324: ULR, ULA, AIR, AIA, PUR, PUA, CLR, CLA
- 8388620-8388621: RAR, RAA

Supported application IDs:
- 0-6: Common, NASREQ, Mobile IPv4, Accounting, Credit Control (Gy), EAP, SIP
- 16777216+: Cx/Dx, Sh, Gx, S6a/S6d, S13, SGd/Gdd, SLg (3GPP)

### 2. Simplified Vendor ID Display
Hid vendor ID 10415 (3GPP) from AVP output for cleaner display.

**Before:**
```
  Bearer-Control-Mode (Code: 1023, Vendor-ID: 10415): 2
  Event-Trigger (Code: 1006, Vendor-ID: 10415): 1
  Charging-Rule-Install (Code: 1001, Vendor-ID: 10415)
```

**After:**
```
  Bearer-Control-Mode (Code: 1023): 2
  Event-Trigger (Code: 1006): 1
  Charging-Rule-Install (Code: 1001)
```

Non-3GPP vendor IDs are still shown when present.

## Example Output

### S6a AIR (Authentication-Information-Request)
```
Diameter Header:
  Version:      1
  Length:       272
  Flags:        0xc0 (Request, Proxiable)
  Code:         318 - AIR (Authentication-Information-Request)
  App ID:       16777251 - S6a/S6d (3GPP)
  Hop-by-Hop:   0xb3de8609
  End-to-End:   0x5581c375

AVPs:
  Session-Id (Code: 263): string-s6a;1407662655052005491;1271062565;69307ee9
  Origin-Host (Code: 264): string
  Origin-Realm (Code: 296): string
  Origin-State-Id (Code: 278): 1620183172
  User-Name (Code: 1): 999991234567810
  Auth-Session-State (Code: 277): 1
  Visited-PLMN-Id (Code: 1407): 0x00f110
  Requested-EUTRAN-Authentication-Info (Code: 1408)
    Number-Of-Requested-Vectors (Code: 1410): 1
    Immediate-Response-Preferred (Code: 1412): 0
  Destination-Realm (Code: 283): magma.com
  Destination-Host (Code: 293): magma-fedgw.magma.com
```

### Gy CCR (Credit-Control-Request)
```
Diameter Header:
  Version:      1
  Length:       768
  Flags:        0xc0 (Request, Proxiable)
  Code:         272 - CCR (Credit-Control-Request)
  App ID:       4 - Diameter Credit Control (Gy)
  Hop-by-Hop:   0x472b5dbc
  End-to-End:   0xfb524fdb

AVPs:
  Session-Id (Code: 263): string;490;022;IMSI999991234567810
  Multiple-Services-Credit-Control (Code: 456)
    Rating-Group (Code: 432): 2
    Requested-Service-Unit (Code: 437)
      CC-Input-Octets (Code: 412): 1000
      CC-Output-Octets (Code: 414): 1000
      CC-Total-Octets (Code: 421): 2000
```

Much cleaner and easier to read!
