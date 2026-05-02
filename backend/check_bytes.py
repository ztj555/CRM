with open('main.py', 'rb') as f:
    lines = f.readlines()
for i, line in enumerate(lines, start=1):
    if b'\xe2\x80\x9c' in line or b'\xe2\x80\x9d' in line or b'\xe2\x80\x98' in line or b'\xe2\x80\x99' in line:
        print(f'Line {i}: {line.rstrip()[:120]}')
