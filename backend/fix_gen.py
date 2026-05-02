#!/usr/bin/env python3
import re

with open('main.py', 'rb') as f:
    data = f.read()

# Find all occurrences of: Depends(get_db
# and check if the next char after 'db' is ASCII quote
pattern = b'Depends\(get_db.'
matches = [m.start() for m in re.finditer(pattern, data)]
print(f'Found {len(matches)} matches of Depends(get_db.*')

fixed = 0
for pos in matches:
    # char right after 'db'
    idx = pos + len(b'Depends(get_db')
    b = data[idx]
    if b != 0x22:  # not ASCII "
        print(f'  Offset {idx}: found 0x{b:02x} after get_db, replacing...')
        # Replace this byte with ASCII "
        data = data[:idx] + b'"' + data[idx+1:]
        fixed += 1

if fixed > 0:
    with open('main.py', 'wb') as f:
        f.write(data)
    print(f'Fixed {fixed} non-ASCII quotes after get_db')
else:
    print('No non-ASCII quotes found after get_db')
    # Check for other issues: scan for all non-ASCII in function def lines
    lines = data.split(b'\n')
    for i, line in enumerate(lines):
        if b'def ' in line or b'):' in line:
            for j, bval in enumerate(line):
                if bval > 127:
                    print(f'  Line {i+1} pos {j}: 0x{bval:02x}')
                    break
