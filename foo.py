from __future__ import print_function
import sys
print('A')
print('B')
print('C', file=sys.stderr)
print('D', file=sys.stderr)

