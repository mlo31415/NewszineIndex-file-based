## Download the requested pages from Fancy 3 on WikiDot

from xmlrpclib import ServerProxy
import codecs, os, sys, pdb

## pdb.set_trace() to set trace points

keys = open('keys.txt')
key = keys.readlines()
keys.close()

request_list = ''; response_list = ''; last_line = ''; legit = '|'; tried = '|'

print ''

for arg in sys.argv:
    if not sys.argv[0] in arg:
        if request_list == '':
            request_list = arg
        elif response_list == '':
            response_list = arg

if response_list == '':
    print '\nGETPAGES request-list response-list (both required)\n'
    sys.exit(0)

page_list     = 'pages.txt'

with open(page_list) as pages:
    for line in pages:
        legit = legit + line.rstrip('\n') + '|'

if os.path.isfile(response_list):
    with open(response_list) as pages:
        for line in pages:
            tried = tried + line.rstrip(' OKX\n') + '|'
            last_line = line

if last_line != '':
    if '\n' not in last_line:
        response = open(response_list, 'a')
        response.write('\n')
        response.close()

s = ServerProxy('https://fancyclopedia:' + key[0].rstrip('\n') +'@www.wikidot.com/xml-rpc-api.php')

ms_dos = '|con|prn|lpt1|'; count = 0
skip = ':admin:deleted:forum:nav:search:system:'

with open(request_list) as pages:
    for line in pages:
        count = count + 1
        line_number = '{0} '.format(count)
        line_number = line_number.rjust(6)

        page_name = line.rstrip('\n')

        if '*' in page_name:
            continue

        if '|' + page_name + '|' in tried:
            continue

        if '|' + page_name + '|' not in legit:
            print '\n' + line_number + ' ' + page_name + ' is not listed in ' + page_list +'\n'
            response = open(response_list, 'a')
            response.write(page_name + ' XX\n')
            response.close()
            continue

        if ':' in page_name:
            work = page_name.partition(':')
            if work[0] in skip:
                continue

        if not '|' + page_name + '|' in ms_dos:
            print line_number + ' ' + page_name
        else:
            print line_number + ' ' + page_name + ' [!' + page_name + '!]'

        response = open(response_list, 'a')
        response.write(page_name + ' ')
        response.close()

        page = s.pages.get_one({'site': 'fancyclopedia', 'page': page_name})

        if '|' + page_name + '|' in ms_dos:
            page_name = '!' + page_name + '!'

        page_file = 'PAGES\\' + page_name.upper().replace(':', '_') + '.SRC'

        target = codecs.open(page_file, 'w', 'CP1252')

        target.write('Title: ' + page['title'] + '\n')
        target.write('Fullname: ' + page['fullname'] + '\n')
        target.write('Created: ' + page['created_by'] + '; ' + page['created_at'] + '\n')
        target.write('Updated: ' + page['updated_by'] + '; ' + page['updated_at'] + '\n')
        target.write('Revisions: {0}\n'.format(page['revisions']))

        target.write('Tags:')
        tags = page['tags']
        for x in tags:
            target.write(' ' + x)
        target.write('\n')

        target.close()

        target = codecs.open(page_file, 'a', 'CP1252')

        content = page['content']
        target.write('Content: ' + content + '\n')
        target.close()

        response = open(response_list, 'a')
        response.write('OK\n')
        response.close()

print ''





