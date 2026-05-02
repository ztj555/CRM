import re

with open('c:/Users/10517/WorkBuddy/20260429105535/screenshots/admin_main.html', 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

# Extract menu items
menus = re.findall(r'data-url="([^"]+)"', html)
names = re.findall(r'data-name="([^"]+)"', html)

print('=== Menu URLs ===')
for m in menus:
    print(' ', m)

print()
print('=== Menu Names ===')
for n in names:
    print(' ', n)

# Extract Open() calls for dynamic menus
opens = re.findall(r"Open\('([^']+)',\s*'([^']+)'\)", html)
print()
print('=== Dynamic Open() calls ===')
for name, url in opens:
    print(f'  {name} -> {url}')

# Extract all hrefs
hrefs = re.findall(r'href="([^"]+)"', html)
print()
print('=== All hrefs ===')
for h in hrefs:
    if 'manage' in h or 'html' in h:
        print(' ', h)
