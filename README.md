# DiaHex2Txt

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub](https://img.shields.io/badge/GitHub-jstdlee%2Fdiahex2txt-181717?logo=github)](https://github.com/jstdlee/diahex2txt)

A powerful CLI tool to decode hex-encoded Diameter protocol messages into human-readable text format with comprehensive 3GPP LTE support.

## Features

- ✅ **Complete AVP Decoding** - Decodes all AVPs in their original wire order
- 🔍 **Smart String Detection** - Automatically decodes UTF-8 strings from bytes
- 📊 **Hierarchical Display** - Shows nested grouped AVPs with proper indentation
- 🏷️ **Protocol Descriptions** - Human-readable command codes and application IDs (30+ command pairs, 30+ interfaces)
- 🎯 **Clean Output** - Simplified vendor ID display (hides 3GPP vendor ID 10415)
- 🔧 **Full 3GPP Support** - Gx, Gy, Rx, S6a/S6d, S9, Sy, SWx, Cx/Dx, Sh, and more!

## Prerequisites

- **Python 3.12+**
- **uv** (Python package and project manager) - [Install uv](https://github.com/astral-sh/uv)

## Installation

1. Clone the repository or navigate to the directory:

```bash
cd diahex2txt
```

2. Install dependencies:

```bash
uv sync
```

3. Install the package (creates `diahex2txt` command):

```bash
uv pip install -e .
```

## Usage

There are three ways to run the decoder:

### Method 1: Using the installed command (After installation)

After running `uv pip install -e .`, the `diahex2txt` command is available:

**Windows (PowerShell/CMD):**
```powershell
# Activate the virtual environment first
.venv\Scripts\activate
# Then use the command directly
diahex2txt <HEX_STRING>

# OR use the full path without activation
.venv\Scripts\diahex2txt.exe <HEX_STRING>
```

**Linux/Mac:**
```bash
# Activate the virtual environment first
source .venv/bin/activate
# Then use the command directly
diahex2txt <HEX_STRING>

# OR use the full path without activation
.venv/bin/diahex2txt <HEX_STRING>
```

### Method 2: Using `uv run` (No installation required)

Works immediately after `uv sync`, no activation needed:

```bash
uv run -m diahex2txt <HEX_STRING>
```

### Method 3: Using wrapper scripts

For convenience, use the provided wrapper scripts:

**Windows:**
```cmd
diahex2txt.bat <HEX_STRING>
```

**Linux/Mac:**
```bash
./diahex2txt.sh <HEX_STRING>
```

### Examples

#### 1. S6a Authentication Information Request (AIR)

```bash
uv run -m diahex2txt 01000110c000013e01000023b3de86095581c375000001074000003a737472696e672d7336613b313430373636323635353035323030353439313b313237313036323536353b36393330376565390000000001084000000e737472696e670000000001284000000e737472696e670000000001164000000c60920884000000014000001739393939393132333435363738313000000001154000000c000000010000057fc000000f000028af00f1100000000580c000002c000028af00000582c0000010000028af0000000100000584c0000010000028af000000000000011b400000116d61676d612e636f6d000000000001254000001d6d61676d612d66656467772e6d61676d612e636f6d000000
```

**Output:**

```
Diameter Header:
  Version:      1
  Length:       272
  Flags:        0xc0 (Request, Proxiable)
  Code:         318 - AIR (Authentication-Information-Request)
  App ID:       16777251 - S6a/S6d (3GPP Mobility Management)
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

#### 2. Gy Credit Control Request (CCR)

```bash
uv run -m diahex2txt 010000c4c0000110000000041122334455667788000001074000000e736573733b3100000000010840000015612e6578616d706c652e636f6d00000000000128400000136578616d706c652e636f6d00000001024000000c00000004000001cd40000016333232353140336770702e6f72670000000001a04000000c000000010000019f4000000c00000000000001c840000038000001b04000000c00000064000001b540000024000001a44000000c00000e10000001a5400000100000000006400000
```

**Output:**

```
Diameter Header:
  Version:      1
  Length:       196
  Flags:        0xc0 (Request, Proxiable)
  Code:         272 - CCR (Credit-Control-Request)
  App ID:       4 - Diameter Credit Control (Gy/Ro)
  Hop-by-Hop:   0x11223344
  End-to-End:   0x55667788

AVPs:
  Session-Id (Code: 263): sess;1
  Origin-Host (Code: 264): a.example.com
  Origin-Realm (Code: 296): example.com
  Auth-Application-Id (Code: 258): 4
  Service-Context-Id (Code: 461): 32251@3gpp.org
  CC-Request-Type (Code: 416): 1
  CC-Request-Number (Code: 415): 0
  Multiple-Services-Credit-Control (Code: 456)
    Rating-Group (Code: 432): 100
    Requested-Service-Unit (Code: 437)
      CC-Time (Code: 420): 3600
      CC-Total-Octets (Code: 421): 104857600
```

#### 3. Stdin, files and several messages

Pass `-` (or no argument) to read stdin. Use a redirect for a file. Several concatenated messages decode as `=== Message N ===` blocks. Whitespace and `0x` prefixes are accepted. The exit code is 1 on any error.

```bash
uv run -m diahex2txt < message.hex
echo 0100001480000110000000040000000000000000 | uv run -m diahex2txt -
```

The command name follows RFC 6733: a request and its answer share one command code, and the R flag selects `CCR` or `CCA`.

## Development

### Running Tests

```bash
uv run --with pytest pytest
```

### Project Structure

```
diahex2txt/
├── diahex2txt/
│   ├── __init__.py
│   ├── __main__.py      # Module entry point
│   ├── main.py          # CLI application
│   └── decoder.py       # Core decoding logic
├── tests/               # Unit tests
├── README.md
├── pyproject.toml       # Project configuration
└── uv.lock             # Dependency lock file
```

## How It Works

1. **Parses the Diameter header** (20 bytes) to extract version, flags, command code, etc.
2. **Manually parses AVPs** directly from raw bytes to preserve wire order
3. **Decodes values** based on AVP data types (UTF-8 strings, integers, grouped AVPs, etc.)
4. **Formats output** with hierarchical indentation for grouped AVPs

## Key Improvements

- ✨ **Complete decoding**: All AVPs are now decoded (previously many were missing)
- 📍 **Wire order preserved**: AVPs appear in their exact transmission order
- 🎨 **Clean display**: Vendor ID 10415 (3GPP) hidden for better readability
- 📝 **Protocol-aware**: Shows human-readable command and application descriptions

## Dependencies

- `python-diameter` - Diameter protocol parsing library
- `typer` - CLI framework

## License

MIT

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.
