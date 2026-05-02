#!/usr/bin/env python3
# This script ONLY uses ASCII characters in its source code.
# It will append clean endpoint code to main.py.

with open('main.py', 'rb') as f:
    data = f.read()

# The new code to append (ASCII only)
new_code = b'''

@api.get("/api/stats/daily-stats")
def get_stats_daily(
    mode: str = Query("daily"),
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    pass  # simplified for testing

'''

# Find where to insert (before 'if __name__ == "__main__":')
marker = b'if __name__ == "__main__":'
idx = data.find(marker)
if idx >= 0:
    # Insert before marker
    new_data = data[:idx] + new_code + data[idx:]
    with open('main.py', 'wb') as f:
        f.write(new_data)
    print('Appended test code')
else:
    print('Marker not found')
