# DiaHex2Txt

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub](https://img.shields.io/badge/GitHub-jstdlee%2Fdiahex2txt-181717?logo=github)](https://github.com/jstdlee/diahex2txt)

A powerful CLI tool to decode hex-encoded Diameter protocol messages into human-readable text format with comprehensive 3GPP LTE support.

## Features

- ✅ **Complete AVP Decoding** - Decodes all AVPs in their original wire order
- 🔍 **Smart String Detection** - Automatically decodes UTF-8 strings from bytes
- 📊 **Hierarchical Display** - Shows nested grouped AVPs with proper indentation
- 🏷️ **Protocol Descriptions** - Human-readable command codes and application IDs (60+ commands, 30+ interfaces)
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
  App ID:       16777251 - S6a/S6d (3GPP)
  Hop-by-Hop:   0xb3de8609
  End-to-End:   0x5581c375

AVPs:
  Session-Id (Code: 263): string-s6a;1407662655052005491;1271062565;69307ee9
  Origin-Host (Code: 264): string
  Origin-Realm (Code: 296): string
  User-Name (Code: 1): 999991234567810
  Visited-PLMN-Id (Code: 1407): 0x00f110
  Requested-EUTRAN-Authentication-Info (Code: 1408)
    Number-Of-Requested-Vectors (Code: 1410): 1
    Immediate-Response-Preferred (Code: 1412): 0
  ...
```

#### 2. Gy Credit Control Request (CCR)

```bash
uv run -m diahex2txt 0100004080000118000000004d8db8f39fbb2d5f000001084000000e737472696e670000000001284000000e737472696e670000000001164000000c60920884
```

**Output:**

```
Diameter Header:
  Version:      1
  Length:       64
  Flags:        0x80 (Request)
  Code:         280 - DWR (Device-Watchdog-Request)
  App ID:       0 - Diameter Common Messages
  Hop-by-Hop:   0x4d8db8f3
  End-to-End:   0x9fbb2d5f

AVPs:
  Origin-Host (Code: 264): string
  Origin-Realm (Code: 296): string
  Origin-State-Id (Code: 278): 1620183172
```

## Development

### Running Tests (not working)

```bash
uv run pytest
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
