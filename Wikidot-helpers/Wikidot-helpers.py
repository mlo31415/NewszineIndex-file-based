# A package to support API access to Wikidot

# *****************************************************************
# Return a Wikidot cannonicized version of a name
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

#*******************************************************************
# Extract something bounded by <string></string>
# tag is not decorated with "<" or ">" or "/"
# String will be treated in a case-insensitive way
def extractTaggedStuff(string, start, tag):
    begin=string.lower().find(start, "<"+tag.lower()+">")
    if begin < start:
        return None

    end=string.lower().find(begin, "</"+tag.lower()+">")
    if end < begin:
        return None

    return string[begin+len(tag)+2:end]
