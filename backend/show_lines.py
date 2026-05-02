#!/usr/bin/env python3
with open('main.py', 'rb') as f:
    data = f.read()

lines = data.split(b'\n')
print(f'Total lines: {len(lines)}')
print('--- Lines 3452-3460 ---')
for i in range(3451, min(3460, len(lines))):
    line = lines[i]
    print(f'Line {i+1} ({len(line)} bytes): {line!r}')
