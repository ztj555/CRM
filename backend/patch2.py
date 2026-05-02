import sys

with open('main.py', 'rb') as f:
    data = f.read()

# Find and replace the broken pattern
old = b'get_db\xe2\x80\x9d)'
new = b'get_db")'

count = data.count(old)
if count > 0:
    data = data.replace(old, new)
    with open('main.py', 'wb') as f:
        f.write(data)
    print(f'Fixed {count} occurrences')
else:
    print('Pattern not found, searching for all non-ASCII...')
    for i, b in enumerate(data):
        if b > 127:
            print(f'  offset {i}: 0x{data[i:i+4].hex()}')
