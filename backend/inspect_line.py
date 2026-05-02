#!/usr/bin/env python3
# Inspect exact bytes at line 3454

with open('main.py', 'rb') as f:
    data = f.read()

# Find line 3454 (1-indexed)
lines = data.split(b'\n')
if len(lines) >= 3454:
    line = lines[3453]  # 0-indexed
    print(f'Line 3454: {len(line)} bytes')
    print(f'Raw bytes: {line.hex()}')
    print(f'As text: {line!r}')
    # Show each byte
    for i, b in enumerate(line):
        ch = chr(b) if b < 128 else '?'
        print(f'  pos {i}: 0x{b:02x} = {ch!r}')
else:
    print(f'File only has {len(lines)} lines')
