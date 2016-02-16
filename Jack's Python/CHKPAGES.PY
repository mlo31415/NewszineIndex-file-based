from xmlrpclib import ServerProxy
## Check pages that are not marked OK in okay.txt

from ftplib import FTP
import codecs, os, sys

keys = open('keys.txt')
key = keys.readlines()
keys.close()

argn = -1; argv = []; print_it = True; save_it = True
print ''

for arg in sys.argv:
    if not sys.argv[0] in arg:
        if '-p' in arg:
            save_it = False
        elif '-s' in arg:
            print_it = False
        else:
            argn = argn + 1
            argv.append(arg)


if argn < 0:
    print 'CHKFILES page [-p] [-s]'
    sys.exit(0)

s = ServerProxy('https://fancyclopedia:' + key[0].rstrip('\n') +'@www.wikidot.com/xml-rpc-api.php')

print ''

ms_dos = 'con prn lpt1'

for page_name in argv:

    print '1 ' + page_name + '\n'

    page = s.pages.get_one({'site': 'fancyclopedia', 'page': page_name})

    if page_name in ms_dos:
        page_name = '!' + page_name + '!'
        print '2 ' + page_name + '\n'

    print page
    print '\n'

    content = page['content']

    if print_it:
        print content
        print '\n'

    if save_it:
        if ':' in page_name:
            page_name = page_name.replace(':', '!')

        target = codecs.open('Test\\' + page_name + '.txt', 'w', 'CP1252')

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

        target = codecs.open('Test\\' + page_name + '.txt', 'w', 'CP1252')

        content = page['content']
        target.write('Content: ' + content + '\n')
        target.close()

        print page_name + '\n'

        with open('Test\\' + page_name + '.txt') as page:
            for line in page:
                print line


