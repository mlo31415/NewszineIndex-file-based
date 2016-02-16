## Download all new/updated pages from Fancy 3 on WikiDot and upload them to fanac.org

## from xmlrpc import ServerProxy
import codecs, os, sys

keys = open('wikidot api access keys.txt')
key = keys.readlines()
keys.close()

## pdb.set_trace() to set trace points

request_list = ''
response_list = ''
last_line = ''
legit = '|'
tried = '|'

print ('')

for arg in sys.argv:
    if not sys.argv[0] in arg:
        if request_list == '':
            request_list = arg
        elif response_list == '':
            response_list = arg

request_list="pages.txt"
response_list="temp.txt"
if response_list == '':
    print ('\nALLPAGES request-list (normally pages.txt) response-list (both required)\n')
    sys.exit(0)

if os.path.isfile(response_list):
    with open(response_list) as pages:
        for line in pages:
            work = line.partition(' ')
            tried = tried + work[0].strip('\n') + '|'
            last_line = line

if last_line != '':
    if '\n' not in last_line:
        response = open(response_list, 'a')
        response.write('\n')
        response.close()

s = ServerProxy('https://fancyclopedia:' + key[0].rstrip('\n') +'@www.wikidot.com/xml-rpc-api.php')

ms_dos = '|con|prn|lpt1|'; count = 0
skip = ':admin:deleted:forum:index:nav:search:system:testing:'

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

        if ':' in page_name:
            work = page_name.partition(':')
            if work[0] in skip:
                continue

        if not '|' + page_name + '|' in ms_dos:
            print (line_number + ' ' + page_name)
        else:
            print (line_number  + ' ' + page_name + ' [!' + page_name + '!]')

        response = open(response_list, 'a')
        response.write(page_name + ' ')
        response.close()

        page = s.pages.get_one({'site': 'fancyclopedia', 'page': page_name})

        if '|' + page_name + '|' in ms_dos:
            page_name = '!' + page_name + '!'

        page_file = 'PAGES\\' + page_name.upper().replace(':', '_') + '.SRC'
        
        go = 1

        if os.path.isfile(page_file):
            with codecs.open(page_file, 'r', 'CP1252') as lines:
                for line in lines:
                    work = line.rstrip('\n').partition(':')
                    if work[0] == 'Updated':                    	
                        work = work[2].partition(';')
                        if cmp(work[2].strip(), page['updated_at']) == 0:
                            go = 0
                        break    	  

        if go == 0:
            response = open(response_list, 'a')
            response.write('OK\n')
            response.close()

        else:
            response = open(response_list, 'a')
            response.write('***\n')
            response.close()

print ('')



