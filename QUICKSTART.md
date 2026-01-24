# Quick Start Guide - DiaHex2Txt

## Installation Steps

```bash
# 1. Navigate to project directory
cd diahex2txt

# 2. Install dependencies
uv sync

# 3. Install the package
uv pip install -e .
```

---

## Usage Methods

### ✅ Method 1: Direct Command (After Installation)

**Best for**: Regular use after installation

```bash
# Windows - Activate venv and run
.venv\Scripts\activate
diahex2txt 0100004080000118000000004d8db8f39fbb2d5f000001084000000e737472696e670000000001284000000e737472696e670000000001164000000c60920884

# Windows - without activation (full path)
.venv\Scripts\diahex2txt.exe 0100004080000118...

# Linux/Mac - Activate venv and run
source .venv/bin/activate
diahex2txt 0100004080000118...

# Linux/Mac - without activation (full path)
.venv/bin/diahex2txt 0100004080000118...
```

---

### ✅ Method 2: Using uv run

**Best for**: Quick usage without installation or activation

```bash
uv run -m diahex2txt 0100004080000118000000004d8db8f39fbb2d5f000001084000000e737472696e670000000001284000000e737472696e670000000001164000000c60920884
```

---

### ✅ Method 3: Wrapper Scripts

**Best for**: Convenience with shorter commands

```bash
# Windows
diahex2txt.bat 0100004080000118...

# Linux/Mac
./diahex2txt.sh 0100004080000118...
```

---

## Example Output

All methods produce the same output:

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

---

## Tip: Adding to System PATH (Optional)

To use `diahex2txt` from anywhere without activation:

**Windows:**
Add `D:\py\diahex2txt\.venv\Scripts` to your PATH environment variable

**Linux/Mac:**
Add to your `~/.bashrc` or `~/.zshrc`:
```bash
export PATH="$PATH:/path/to/diahex2txt/.venv/bin"
```

Then you can simply run:
```bash
diahex2txt <HEX_STRING>
```
from any directory!
