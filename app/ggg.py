import re

pattern = r"^\\(?!\\)"

text = ['\images', "\\\\images", 'test']

for w in text:
    print(re.match(pattern, w))
