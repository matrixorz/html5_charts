

import math
import json

out = {}

for i in range(0,12):
    print i, math.sin(i)
    out[i]=math.sin(i)

print json.dumps(out)

from datetime import datetime

datestr = json.dumps(datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))

print datestr

print json.loads(datestr) 
