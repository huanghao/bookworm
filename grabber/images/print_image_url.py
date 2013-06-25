import sys
import json

for line in sys.stdin:
    data = json.loads(line)
    print data['cover_link']
