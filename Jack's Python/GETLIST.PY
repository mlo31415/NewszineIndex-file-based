## Download a list of the pages that are currently availiable
## form Fancy 3 on WikiDot

from xmlrpclib import ServerProxy
import os, sys

keys = open('keys.txt')
key = keys.readlines()
keys.close()

argn = -1; argv = []

print('')

for arg in sys.argv:
    if not sys.argv[0] in arg:
        argn = argn + 1
        argv.append(arg)

if argn < 0:
    print('\nGETLIST requires an operand to run\n')
    sys.exit(0)


file_name = 'PAGES.TXT'

s = ServerProxy('https://fancyclopedia:' + key[0].rstrip('\n') +'@www.wikidot.com/xml-rpc-api.php')

target = open(file_name, "w")

files = s.pages.select({"site": "fancyclopedia"})

files.sort()

count = 0

for line in files:
    target.write(line + "\n")
    count = count + 1

target.close()

print('\n{0} downloaded, it contains {1} page names.\n'.format(file_name, count))
