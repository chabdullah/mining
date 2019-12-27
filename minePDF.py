import re

text = re.sub('<[^<]+>', "", open("./").read())
with open("/path/to/file", "w") as f:
    f.write(text)
