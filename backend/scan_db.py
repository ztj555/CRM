with open('main.py', 'rb') as f:
    data = f.read()

# Find all occurrences of 'get_db' and check following bytes
idx = 0
while True:
    idx = data.find(b'get_db', idx)
    if idx < 0:
        break
    # Show bytes around this position
    start = max(0, idx - 5)
    end = min(len(data), idx + 15)
    print(f"Found 'get_db' at offset {idx}")
    print(f"  Context: {data[start:end].hex()}")
    print(f"  As text: {data[start:end]!r}")
    idx += 1

print("Done scanning.")
