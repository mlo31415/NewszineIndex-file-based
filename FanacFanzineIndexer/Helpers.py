#*******************************************************************
# Extract something bounded by <string></string>
# tag is not decorated with "<" or ">" or "/"
# The opening tag is assumed to be of the form "<tag...>" (where "..." is random stuff)
# The closing tag is assumed to be "</tag>"
# String will be treated in a case-insensitive way
def extractTaggedStuff(string, start, tag):
    begin=string.lower().find("<"+tag.lower(), start)
    if begin < start:
        return None
    # Now find the closing ">" for the opening tag.
    begin=string.find(">", begin)
    if begin == -1:
        return None
    begin=begin+1   # Need to skip over the ">"

    end=string.lower().find("</"+tag.lower()+">", begin)
    if end < begin:
        return None

    # We return a tuple, containing the string found and the ending position of the string found in the input string
    return (string[begin:end], end+len(tag)+3)
