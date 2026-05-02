#!/usr/bin/env python3
# Fix: get_db" -> get_db)"
import sys

with open('main.py', 'rb') as f:
    data = f.read()

old = b'get_db"'
new = b'get_db)'

count = data.count(old)
if count > 0:
    data = data.replace(old, new)
    with open('main.py', 'wb') as f:
        f.write(data)
    print(f'Fixed {count} occurrences: get_db" -> get_db)"')
else:
    print('Pattern get_db" not found, checking...')
    # Maybe it's get_db with right parenthesis missing
    if b'get_db"' in data:
        print('Found get_db"')
    else:
        print('get_db" not in file')

# Now check if there are actual Unicode quotes
import re
matches = list(re.finditer(b'Depend\(get_db.', data))
print(f'Found {len(matches)} Depend(get_db.* patterns')
for m in matches[:3]:
    idx = m.start() + len(b'Depend\(get_db')
    b = data[idx]
    print(f'  After get_db at offset {idx}: 0x{b:02x} = {chr(b) if b < 128 else "?"}')
