#*******************************************************************
# Extract something bounded by <string></string>
# tag is not decorated with "<" or ">" or "/"
# String will be treated in a case-insensitive way
def extractTaggedStuff(string, start, tag):
    begin=string.lower().find("<"+tag.lower()+">", start)
    if begin < start:
        return None

    end=string.lower().find("</"+tag.lower()+">", begin)
    if end < begin:
        return None

    return string[begin+len(tag)+2:end]
