import re


def firstint(s):
    if s[0].startswith('<'):
        return 0
    m = re.search(r'\d+', s[0])
    return int(m.group(0))
