import sys

# Read as binary
with open('main.py', 'rb') as f:
    data = f.read()

# Replace UTF-8 encoded Unicode quotes with ASCII quotes
# \u201c (left double quote) -> "
data = data.replace(b'\xe2\x80\x9c', b'"')
# \u201d (right double quote) -> "
data = data.replace(b'\xe2\x80\x9d', b'"')
# \u2018 (left single quote) -> '
data = data.replace(b'\xe2\x80\x98', b"'")
# \u2019 (right single quote) -> '
data = data.replace(b'\xe2\x80\x99', b"'")

with open('main.py', 'wb') as f:
    f.write(data)

print('Done - fixed all Unicode quotes')
