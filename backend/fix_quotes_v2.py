import sys

with open('main.py', 'rb') as f:
    data = f.read()

# Only fix Unicode smart quotes (UTF-8 sequences)
patterns = [
    (b'\xe2\x80\x9c', b'"'),   # left double quote
    (b'\xe2\x80\x9d', b'"'),   # right double quote
    (b'\xe2\x80\x98', b"'"),   # left single quote
    (b'\xe2\x80\x99', b"'"),   # right single quote
]

total = 0
for old, new in patterns:
    cnt = data.count(old)
    if cnt > 0:
        data = data.replace(old, new)
        total += cnt
        print(f'Replaced {cnt} occurrences of {old.hex()}')

print(f'Total fixed: {total}')
    
with open('main.py', 'wb') as f:
    f.write(data)
