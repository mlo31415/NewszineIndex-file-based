# coding: CP1252

## Upload the requested pages to Fancy 3 on WikiDot

from xmlrpclib import ServerProxy
import codecs, os, sys, pdb

## pdb.set_trace() to set trace points

keys = open('keys.txt')
key = keys.readlines()
keys.close()

request_list = ''; response_list = ''; last_line = ''; tried = '|'; debug = 0

print ''

for arg in sys.argv:
    if not sys.argv[0] in arg:
        if '-d:' in arg:
            debug = arg.lstrip('-d:')
        elif request_list == '':
            request_list = arg
        elif response_list == '':
            response_list = arg

if response_list == '':
    print '\nPUTPAGES request-list response-list (both required)\n'
    sys.exit(0)

if os.path.isfile(response_list):
    with open(response_list) as pages:
        for line in pages:
            tried = tried + line.strip(' *OKX\n') + '|'
            last_line = line

if last_line != '':
    if '\n' not in last_line:
        response = open(response_list, 'a')
        response.write('\n')
        response.close()

s = ServerProxy('https://fancyclopedia:' + key[0].rstrip('\n') +'@www.wikidot.com/xml-rpc-api.php')

ms_dos = '|con|prn|lpt1|'; count = 0

with open(request_list, 'r') as files:
    for line in files:

        file_name = line.rstrip('\n')

        if file_name == '':
            continue

        count = count + 1

        if '*' in file_name:
            continue

        work = file_name.partition('.')
        page_name = work[0]

        if '|' + page_name + '|' in tried:
            continue

        if '|' + page_name + '|' in ms_dos:
            page_name = '!' + page_name + '!'

        page_file = 'PAGES\\' + page_name.upper().replace(':', '_') + '.SRC'

        title = ''; fullname = ''; content = ''; size = 0; comment = '?'; ## tags.array('c', ' ')

        response = open(response_list, 'a')
        response.write(page_name + ' ')
        response.close()

        with codecs.open(page_file, 'r', 'CP1252') as lines:
            for line in lines:
                work = line.rstrip('\n').partition(':')
                if work[0] == 'Title':
                    title = U"%s"%(work[2])
                    size = size + len(title) + 7
                elif work[0] == 'Fullname':
                    fullname = work[2]
                    size = size + len(title) + 10
                ##elif work[0] == 'Tags':
                  ##tags.array('c', work[2])
                  ##size = size + len(work[2]) + 5
                elif work[0] == 'Notify':
                    comment = work[2]
                    size = size + len(work[2]) + 39
                elif work[0] == 'Content':
                    content = U"%s"%(work[2].strip()) + '\n'
                    size = size + len(content) + 9
                elif work[0] == '[-- EA':
                    size = size + 0
                elif content != '':
                    work = U"%s"%(line.strip()) + '\n'
                    size = size + len(work)
                    content = content + work


        print ' %5d %7d  %s'%(count, size, page_name.replace('_', ':'))

        if comment == '?':
            page = s.pages.save_one({'site': 'fancyclopedia', 'page': fullname, 'title': title, 'content': content})
        elif comment == '':
            page = s.pages.save_one({'site': 'fancyclopedia', 'page': fullname, 'title': title, 'content': content, 'notify_watchers': (size > 0)})
        else:
            page = s.pages.save_one({'site': 'fancyclopedia', 'page': fullname, 'title': title, 'content': content, 'notify_watchers': (size > 0), 'revision_comment': comment})

        ## Replace the original file with the one returned from WikiDot

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

