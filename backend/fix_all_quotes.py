#!/usr/bin/env python3
# Fix Unicode smart quotes in main.py
# This script only uses ASCII characters in its source code

import sys

with open('main.py', 'rb') as f:
    data = f.read()

# Unicode smart quotes to ASCII
# Left double quote \u201c -> "
# Right double quote \u201d -> "  
# Left single quote \u2018 -> '
# Right single quote \u2019 -> '

replacements = [
    (b'\xe2\x80\x9c', b'"'),   # left double quote
    (b'\xe2\x80\x9d', b'"'),   # right double quote
    (b'\xe2\x80\x98', b"'"),   # left single quote
    (b'\xe2\x80\x99', b"'"),   # right single quote
]

total = 0
for old, new in replacements:
    cnt = data.count(old)
    if cnt > 0:
        data = data.replace(old, new)
        total += cnt
        print(f'Replaced {cnt} occurrences of {old.hex()}')

print(f'Total fixed: {total}')

with open('main.py', 'wb') as f:
    f.write(data)

print('Done. Running syntax check...')

import subprocess
result = subprocess.run(
    [r'C:\Users\10517\.workbuddy\binaries\python\versions\3.13.12\python.exe', '-m', 'py_compile', 'main.py'],
    capture_output=True, text=True
)
if result.returncode == 0:
    print('Syntax OK!')
else:
    print('Syntax error:')
    print(result.stdout)
    print(result.stderr)
