#!/usr/bin/env python3
#
# GPS test
#

import sys
import errno
import json


try:
  while True:
    line = sys.stdin.readline()
    if not line: break # EOF

    sentence = json.loads(line)
    if sentence['class'] == 'TPV':
      sys.stdout.write(str(sentence['lat']) + ',' + str(sentence['lon']) + ',' + str(sentence['alt']) + ',' + str(sentence['time']) + '\n')
      sys.stdout.flush()
except IOError as e:
  if e.errno == errno.EPIPE:
    pass
  else:
    raise e
