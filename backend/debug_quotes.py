#!/usr/bin/env python3
import re

with open('main.py', 'rb') as f:
    data = f.read()

# Find ALL occurrences of Depends(get_db followed by any char that is non-ASCII
pattern = b'Depends\(get_db.'
matches = [m.start() for m in re.finditer(b'Depends\(get_db.', data)]
print(f'Found {len(matches)} matches of Depends(get_db.*')

for pos in matches:
    # Show the next 15 bytes
    chunk = data[pos:pos+40]
    print(f'  Offset {pos}: {chunk.hex()}')
    # Check if the byte after 'db' is ASCII quote (0x22) or something else
    db_end = pos + len(b'Depends(get_db')
    b = data[db_end]
    qchar = chr(b) if b < 128 else '?'
    print(f'    char after db: 0x{b:02x} = {qchar!r}')

# Now fix: replace non-ASCII quote after db with ASCII quote
fixed = 0
for pos in matches:
    db_end = pos + len(b'Depends(get_db')
    b = data[db_end]
    if b != 0x22:  # not ASCII double quote
        # Check if it's a Unicode quote
        if data[db_end:db_end+3] == b'\xe2\x80\x9c':
            data = data[:db_end] + b'"' + data[db_end+3:]
            fixed += 1
        elif data[db_end:db_end+3] == b'\xe2\x80\x9d':
            data = data[:db_end] + b'"' + data[db_end+3:]
            fixed += 1

if fixed > 0:
    with open('main.py', 'wb') as f:
        f.write(data)
    print(f'Fixed {fixed} non-ASCII quotes after get_db')

# Now check all function signatures for unterminated strings
# Look for: Depends(get_current_user) and Depends(get_db) patterns
print('\nDone checking.')
