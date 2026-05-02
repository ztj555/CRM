import sys

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace Unicode quotes with ASCII quotes
content = content.replace('\u201c', '"').replace('\u201d', '"').replace('\u2018', "'").replace('\u2019', "'")

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done - fixed Unicode quotes')
