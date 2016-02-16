import os, sys, string
import tkinter as tk
from tkinter import filedialog
import zipfile
import time

log = open("log.txt", "w")


# *****************************************************************
# Return a Wikidot cannonicized version of the name
# The cannonicized name turns all spans of non-alphanumeric characters into a single hyphen, drops all leading and trailing hyphens
# and turns all alphabetic characters to lower case
cannonicalToReal = {}   # A dictionary which lets us go from cannonical names to real names
def Cannonicize(pageNameRaw):
    if pageNameRaw == None:
        return None
    name = pageNameRaw.lower()
    # The strategy is to iterate through name, copying characters to a list of characters (appending to a string is too expensive)
    out = []
    inAlpha = False
    inJunk = False
    for c in name:
        if c.isalnum():
            if inJunk:
                out.append("-")
            out.append(c)
            inJunk = False
            inAlpha = True
        else:
            inJunk = True
            inAlpha = False
    canName=''.join(out)
    if cannonicalToReal.get(canName) == None:
        cannonicalToReal[canName]=pageNameRaw  # Add this cannonical-to-real conversion to the dictionary
    return canName


# *****************************************************************
# Potnetially add this entry to the list of uncannonicized page names
def AddUncannonicalName(uncanName, canName):
    if cannonicalToReal.get(canName) == None:
        cannonicalToReal[canName]=uncanName
    else:
        if ([x.isupper() for x in uncanName].count(True) > [x.isupper() for x in cannonicalToReal[canName]].count(True)):
            cannonicalToReal[canName]=uncanName


# *****************************************************************
def Uncannonicize(name):
    n=cannonicalToReal.get(name)
    if n != None:
        return n

    # OK, this is most likely the name of a redirect page.  The best we can do is to remove internal hyphens.
    # (We need to do better here!)
    return name.replace("-", "")


# *****************************************************************
#  Is the page a redirect?  If yes, return the cannonicized redirect; if not, return null
# A redirect is of the form [[module Redirect destination=""]]
def IsRedirect(pageText):
    pageText = pageText.strip()  # just to be safe, remove leading and trailing whitespace
    if pageText.lower().startswith('[[module redirect destination="') and pageText.endswith('"]]'):
        return Cannonicize(pageText[31:].rstrip('"]'))
    return None


# *****************************************************************
# Should this filename be ignored?
def interestingFilenameRaw(filenameRaw):
    if not filenameRaw.startswith("source/"):
        return None
    if len(filenameRaw) <= 11:  # There needs to be something there besides 'source/.txt'
           return None
    if filenameRaw.startswith("source/index_people"):  # Pages with names "source/index_people..." are index pages, not content pages.
        return None
    if filenameRaw.startswith("source/index_alphanumeric"):  # Likewise
        return None
    if filenameRaw.startswith("source/testing_alphanumeric"):  # Likewise
        return None
    return filenameRaw[7:-4]  # Drop "source/" and ".txt"


# *****************************************************************
# Read a source file from the zip
def readSource(zip, filename):

    if interestingFilenameRaw(filename) == None:
        return None

    source = zip.read(filename).decode("utf-8")
    if source == None:
        print("error: '" + filename + "' read as None")
        exit
    return source


# *****************************************************************
# *****************************************************************
# Main
# Navigate to zipped backup file to be analyzed, open it, and read it
root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename()
if not zipfile.is_zipfile(file_path):
    exit()
zip = zipfile.ZipFile(file_path)

# redirects is a dictionary of redirects.  The key is a cannonicized name, the value is the cannonicized name that it is redirected to.
redirects = {}

pageChildren = {}   # Dictionary of pageChildren. The key is the cannonicized page name. The value is a list of cannonicized pages referred to on that page
countPages=0        # Count of all pages with content, including redirects
pagesNames=[]       # List of cannonicized page names

# Walk through the zip file, looking only at source pages.
zipEntryNames = zip.namelist()
for zipEntryName in zipEntryNames:
    nameRaw=interestingFilenameRaw(zipEntryName)
    if nameRaw == None:
        continue
    source = readSource(zip, zipEntryName)
    if source == None:
        continue

    countPages += 1
    pagesNames.append(Cannonicize(nameRaw)) # Create the list of all cannonicized, interesting names: Both content pages and redirects

    # Is this a redirect?
    redir = IsRedirect(source)
    if redir != None:
        # If so, add it to the redirect dictionary (remember to remove the extension!)
        name=Cannonicize(nameRaw)
        if name == redir:  # Skip circular redirects
            continue
        redirects[name] = redir
        continue

countRedirects=len(redirects)
countPages=len(pagesNames)
# Now we need to trace all the redirect chains  and make sure that every redirect points to the end of its chain.
# I.e., right now we have a->b, b->c.  We want this to be a->c and b->c.
for n in redirects:
    while redirects.get(redirects[n]) != None:  # Is the page we're redirecting to also a redirect?
        redirects[n] = redirects[redirects[n]]

print("Redirects analysis complete: redirects.len=", countRedirects)

# Next we go through the *non*-redirect pages and create a list of their references
pagesRefs = {}  # The dictionary of pages, each holding a list of references for that page
refsPages = {}  # The dictionary of references, each holding a list of pages that reference it
countContentPages=0
for zipEntryName in zipEntryNames:
    uncanName=interestingFilenameRaw(zipEntryName)
    name=Cannonicize(uncanName)
    if name == None:
        continue
    if redirects.get(name) != None:  # Skip redirects
        continue

    # Load the page source
    source = readSource(zip, zipEntryName)  # Skip empty pages
    if source == None or len(source) == 0:
        print("error: Page '"+zipEntryName+"' is empty.", file=log)
        continue

    # We need to find all the references in the page.  A reference is a string inside a pair of triple square brackets, i.e., [[[string]]]
    # We'll start by spliting the page on "[[[". This will yield a list of strings, each starting with a reference which ends with "]]]", usually followed by junk.
    splitSource = source.split("[[[")
    refs = []       # Refs will be a list of all the references found in this source page
    for r in splitSource:
        if r.find("]]]") < 1:   # If the string doesn't contain reference closing brackets ("]]]"), then it's a leading string of junk which must be skipped.
            continue
        ref = r.split("]]]")    # If it does contain "]]]", then there's a reference to be found.  The format of the string is <reference>]]]<trailing stuff>.
        if ref == None or len(ref) <= 1:    # If there's nothing to be found, skip it.
            continue
        if ref[0] != None and len(ref) > 0: # The part we want ("<reference>" from the comment above) will be in ref[0].  Make sure it exists.
            if ref[0].find("|") > 0:    # Look for references containing "|".  These are of the form <reference name>|<display name>.  We want just the reference name.
                ref[0]=ref[0][:ref[0].find("|")]
            refCan=Cannonicize(ref[0])
            refs.append(refCan)
            AddUncannonicalName(ref[0], refCan)

    countContentPages += 1

    # Take all the references we've collected from this source page, make sure any redirects are followed, and update the refPages dict.
    # RefsPages[name] contains a list of all pages which refer *to* the source pages "name".
    rrefs = []
    for r in refs:  # r is a reference to another page contained in page n
        if redirects.get(r) == None:    # Make sure each ref is fully redirected
            rrefs.append(r)
        else:
            rrefs.append(redirects[r])

        if refsPages.get(r) == None:
            refsPages[r]=[]
        refsPages[r].append(name)

    # PagesRefs[name], OTOH, contains a list of all pages referred to by source page "name"
    pagesRefs[name] = rrefs

print("Source reference analysis complete:", len(pagesRefs), "pages found with references")

# We now have a list of all content pages and each of those pages has a list of pages referenced
# We want to gather some statistics and make some lists of interesting pages:
# * How many pages total? (names.len())
# * How many content pages?  (names.len()-redirects.len())
# * How many redirects?     (redirects.len())
# * How many references total?
# * How many missing pages?
# * List of all missing pages references 10 or more times
# * List of most referenced pages

# We need to count the number of references each page has.
countTotalRefs = 0
countRefs = {}  # A dictionary of pages with reference counts for that page
for name in pagesNames:
    if pagesRefs.get(name) != None:
        for r in pagesRefs[name]:
            if countRefs.get(r) == None:
                countRefs[r] = 0
            countRefs[r] += 1
            countTotalRefs += 1

# It's output time!
# We'll prepend the file name with the date.  Get the date string
day=time.strftime("%Y-%m-%d")

# Summary statistics
file=open(day+" Summary Statistics.txt", "w")
print("||||~ Summary Statistics ||", file=file)
print("||~ Kind ||~ Number ||~ Notes ||", file=file)
print("|| Pages with content ||", countContentPages, "|| All pages that have text on them. ||", file=file)
print("|| Redirects ||", countRedirects, "|| Pages which redirect to a content page. (The content page itself does not necessarily yet exist.) ||", file=file)
print("|| Total existing pages ||", countPages, "|| Pages with content plus redirects ||", file=file)
print("|| Pages still needed ||", len(refsPages)-countContentPages-countRedirects, "|| Pages which are referred to, but which have not yet been created ||", file=file)
print("|| Total references ||", countTotalRefs, "|| A count of how many links to other pages exist in all existing pages ||", file=file)
file.close()

# Most Referenced Pages
file=open(day+" Most Referenced Pages.txt", "w")

# We generate one line in the table for each *value* of reference count (i.e., all pages with 50 references are in a single row of the table.)
# First sort countRefs into descending order.  To do this, we turn it into a list of tuples(name, count)
countRefTuples = []
for name in countRefs:
    countRefTuples.append((name, countRefs[name]))
countRefTuples.sort(key=lambda n: n[1], reverse=True)

currentNum=-1
line=""
for crt in countRefTuples:
    if crt[1] != currentNum:
        if len(line)>0:
            print("||", currentNum, "||", line, "||", file=file)
            line=""
        currentNum=crt[1]

    if currentNum <= 7:
        break

    if len(crt[0]) == 4 and crt[0].isdecimal() and (crt[0].startswith("19") or crt[0].startswith("20")):
        continue    # Skip the year entries
    if len(line)>0:
        line=line+", "  # The first entry is not preceded by a comma
    line=line+"[[["+Uncannonicize(crt[0])+"]]]"

file.close()

# Most requested pages
file=open(day+" Most Wanted Pages.txt", "w")

# Go through the dictionary and copy just the tuples missing pages.
missingPages=[]
for crt in countRefTuples:
    if pagesRefs.get(crt[0]) == None:
        missingPages.append(crt)

# Sort what's left
missingPages.sort(key=lambda n: n[1], reverse=True)

# We generate one line in the table for each *value* of reference count (i.e., all pages with 50 references are listed in a single row of the table.)
currentNum=-1
line=""
for mp in missingPages:
    if mp[1] != currentNum:
        if len(line)>0:
            print("||", currentNum, "||", line, "||", file=file)
            line=""
        currentNum=mp[1]

    if currentNum <= 5:
        break

    if len(line)>0:
        line=line+", "
    line=line+"[[["+Uncannonicize(mp[0])+"]]]"

file.close()

# Print the list of all references
file=open(day+" Pages.txt", "w")
for name in pagesNames:
    print(Uncannonicize(name), file=file)
file.close()

exit

