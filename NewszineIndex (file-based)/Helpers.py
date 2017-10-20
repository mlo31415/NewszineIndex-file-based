from datetime import datetime
import re

# Remove certain strings which amount to whitespace
import timestring as timestring


def RemoveDebris(str):
    str=str.replace("<BR>", "")
    return str.replace("<br>", "")


def InterpretYear(yearstring):
    yearstring=RemoveDebris(yearstring)
    if len(yearstring) == 0:
        return None
    try:
        year=int(yearstring)
    except:
        print("   ***Year conversion failed: '" + yearstring+"'")
        year=None
    return year


def InterpretDay(daystring):
    daystring=RemoveDebris(daystring)
    if len(daystring) == 0:
        return None
    try:
        day=int(daystring)
    except:
        print("   ***Day conversion failed: '" + daystring+"'")
        day=None
    return day


def InterpretMonth(monthstring):
    monthstring=RemoveDebris(monthstring)
    if len(monthstring) == 0:
        return None
    monthConversionTable={"jan" : 1, "january" : 1, "1" : 1,
                          "feb" : 2, "february" : 2, "2" : 2,
                          "mar" : 3, "march" : 3, "3" : 3,
                          "apr" : 4, "april" : 4, "4" : 4,
                          "may" : 5, "5" : 5,
                          "jun" : 6, "june" : 6, "6" : 6,
                          "jul" : 7, "july" : 7, "7" : 7,
                          "aug" : 8, "august" : 8, "8" : 8,
                          "sep" : 9, "sept" : 9, "september" : 9, "9" : 9,
                          "oct" : 10, "october" : 10, "10" : 10,
                          "nov" : 11, "november" : 11, "11" : 11,
                          "dec" : 12, "december" : 12, "12" : 12,
                          "1q" : 1,
                          "4q" : 4,
                          "7q" : 7,
                          "10q" : 10,
                          "spring" : 4,
                          "summer" : 7,
                          "fall" : 10, "autumn" : 10,
                          "winter" : 1,
                          "january-february" : 2,
                          "march-april" : 4,
                          "april-may" : 5,
                          "apr-may" : 5,
                          "may-june" : 6,
                          "july-august" : 8,
                          "august-september" : 9,
                          "september-october" : 10,
                          "sep-oct" : 10,
                          "october-november" : 11,
                          "oct-nov" : 11,
                          "september-december" : 12,
                          "november-december" : 12,
                          "december-january" : 12,
                          "dec-jan" : 12}
    try:
        month=monthConversionTable[monthstring.replace(" ", "").lower()]
    except:
        print("   ***Month conversion failed: "+monthstring)
        month=None
    return month

# Interpret a free-form date string
# We will assume no time information
def InterpretDateString(datestring):
    # We will try a series of possible formats
    try:
        return timestring.date(datestring)
    except:
        pass

    try:
        return int(datestring)  # Just a bare number.  It pretty much has to be a year.
    except:
        pass

    try:
        return datetime.strptime(datestring, '%b %Y')   # 'Jun 2005'
    except:
        pass

    try:
        return datetime.strptime(datestring, '%B %Y')   # 'June 2005'
    except:
        pass

    try:
        # Look at the case of exactly two tokens, and the second is a year-like number (E.g., June 1987)
        d=datestring.split(" ")
        try:
            y=int(d[1])
            m=InterpretMonth(d[0])
            return datetime(y, m, 1)
        except:
            pass
    except:
        pass
    return None


def CannonicizeColumnHeaders(header):
    # 2nd item is the cannonical form
    translationTable={"title" : "title",
                      "issue" : "issue",
                      "month" : "month",
                      "mo." : "month",
                      "day" : "day",
                      "year" : "year",
                      "repro" : "repro",
                      "editor" : "editor",
                      "editors" : "editor",
                      "notes" : "notes",
                      "pages" : "pages",
                      "page" : "pages",
                      "size" : "size",
                      "type" : "type",
                      "#" : "#",
                      "no" : "#",
                      "number" : "#",
                      "vol" : "vol",
                      "volume" : "vol",
                      "num" : "num",
                      "headline" : "headline",
                      "publisher" : "publisher",
                      "published" : "date"}
    try:
        return translationTable[header.replace(" ", "").lower()]
    except:
        print("   ***Column Header conversion failed: '" + header + "'")
        return None


def RecognizeDescritpionBlockStart(line):
    starters={"<p>", "<h2>", "<h3>"}
    line=line.lower()
    for starter in starters:
        if len(line) > len(starter) and line[:len(starter)] == starter:
            return True
    return False


def RecognizeDescriptionBlockEnd(line):
    enders={"</p>", "</h2>", "</h3>"}
    line=line.lower()
    for ender in enders:
        if len(line) > len(ender) and line[-len(ender):] == ender:
            return True
    return False


# Find text bracketed by <b>...</b>
# Return the contents of the first pair of brackets found and the remainder of the input string
def FindBracketedText(s, b):
    strlower=s.lower()
    l1=strlower.find("<"+b.lower())
    if l1 == -1:
        return "", ""
    l1=strlower.find(">", l1)
    if l1 == -1:
        print("***Error: no terminating '>' found in "+strlower+"'")
        return "", ""
    l2=strlower.find("</"+b.lower()+">", l1+1)
    if l2 == -1:
        return "", ""
    return s[l1+1:l2], s[l2+3+len(b):]


# Find an element in a list of strings using case-insensitive compares and return its index or -1 if not present
def FindStringInList(list, el):
    i=0
    for s in list:
        if s.lower() == el.lower():
            return i
        i=i+1
    return -1


# Decode a hyperlink by returning the hyperlink's target and the display text
def DecodeHyperlink(title):
    # Now we decode the title to pull out the URL and displayname
    # Start by ignoring everything before the HREF=
    loc = title.lower().find("href=")
    if loc == -1:
        print("   ***Can't decode (1) title=" + title)
        return
    title = title[loc + 5:]
    # What's left should begin with a '"' and end with </A>.  Delete them both
    if title[0] == '"':
        title = title[1:]
    if title.lower()[-4:] == "</a>":
        title = title[:-4]
    # Now we should have filename.html followed by '">' followed by displayname
    loc = title.find('">')
    if loc == -1:
        print("  ***Can't decode (2) title=" + title)
        return
    s = title.split('">')
    if len(s) != 2:
        print("  ***Can't decode (3) title=" + title)
        return
    return s