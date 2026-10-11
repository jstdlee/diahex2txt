# Diameter Decoder - Update Summary

## Problem
The decoder was not showing all AVPs and wasn't preserving the original wire order of AVPs in Diameter messages.

### Root Cause
The `python-diameter` library parses typed messages (e.g., `CreditControlAnswer`, `CreditControlRequest`) and **consumes** the raw AVPs from the `_avps` list into typed attributes. This caused two issues:
1. **Missing AVPs**: Not all AVPs were being displayed
2. **Lost order**: The original wire order was lost because Python dict iteration doesn't guarantee AVP order

## Solution
Implemented manual AVP parsing directly from the raw bytes when `_avps` is empty:

1. **Direct byte parsing**: Added `_parse_avps_from_bytes()` method that uses `Unpacker` to parse AVPs directly from the binary data
2. **Order preservation**: By parsing from bytes, we maintain the exact order AVPs appeared on the wire
3. **Complete decoding**: All AVPs are now decoded, not just the ones that map to typed attributes

## Changes Made
- Modified `decoder.py` to check if `_avps` is empty
- When empty, parse AVPs manually from raw bytes (skipping the 20-byte Diameter header)
- Enhanced string decoding for bytes values (UTF-8 with fallback to hex)
- Added datetime/date/time as simple types to prevent recursion errors
- Improved nested object formatting with proper indentation

## Test Results
All 4 sample messages from `samples.txt` now decode completely:
- Sample 1: 61 AVPs decoded (was showing only 16 attributes)
- Sample 2: 11 AVPs decoded  
- Sample 3: 40 AVPs decoded
- Sample 4: 59 AVPs decoded

All AVPs preserve their original wire order and display correctly with:
- Proper indentation for grouped AVPs
- Field-per-line formatting for complex structures
- UTF-8 string decoding where applicable
- Hex fallback for binary data
