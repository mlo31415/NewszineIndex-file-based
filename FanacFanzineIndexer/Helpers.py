import datetime
from calendar import monthrange


#*******************************************************************
# Extract something bounded by <string></string>
# tag is not decorated with "<" or ">" or "/"
# The opening tag is assumed to be of the form "<tag...>" (where "..." is random stuff)
# The closing tag is assumed to be "</tag>"
# String will be treated in a case-insensitive way
def ExtractTaggedStuff(string, start, tag):
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


# ---------------------------------------------------------------------
def Date(year, month, day):
    if day == None  or  month == None or year == None:
        return None

    # We want to deal with days that are just outside the month's range -- anything more than about 10 days is probably not deliberate,
    # but some sort of parsing error feeding in garbage data.

    # First deal with dates later than the month's range
    dayrange=monthrange(year, month)
    if day > dayrange[1] and day <40:
        day=day-dayrange[1]
        month=month+1
        if month > 12:
            month=month-12
            year=year+1

    # Now deal with days before the start of the month
    if day < 1 and day > -10:
        month=month-1
        if month < 1:
            month=12
            year=year-1
        dayrange=monthrange(year, month)
        day=dayrange[1]-day

    # Returning you now to your mundane date function...
    return datetime.datetime(year, month, day).date()


# ---------------------------------------------------------------------
def InterpretInt(intstring):
    try:
        return int(intstring)
    except:
        return None

#---------------------------------------------------------------------
def InterpretYear(yearstring):
    # Remove leading and trailing cruft
    cruft=['.']
    while len(yearstring) > 0  and  yearstring[0] in cruft:
        yearstring=yearstring[1:]
    while len(yearstring) > 0  and  yearstring[:-1] in cruft:
        yearstring=yearstring[:-1]

    # Handle 2-digit years
    if len(yearstring) == 2:
        year2=InterpretInt(yearstring)
        if year2 == None:
            return None
        if year2 < 30:  # We handle the years 1930-2029
            return 2000+year2
        return 1900+year2

    # 4-digit years are easier...
    if len(yearstring) == 4:
        return InterpretInt(yearstring)

    return None

#---------------------------------------------------------------------
def InterpretMonth(monthstring):
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
                          "winter": 1,
                          "spring" : 4,
                          "summer" : 7,
                          "fall" : 10, "autumn" : 10,
                          "january-february" : 2,
                          "january/february" : 2,
                          "winter/spring" : 3,
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
        return monthConversionTable[monthstring.replace(" ", "").lower()]
    except:
        return None

#-----------------------------------------------------
# Handle dates like "Thanksgiving"
# Returns a month/day tuple which will often be exactly correct and rarely off by enough to matter
# Note that we don't (currently) attempt to handle moveable feasts by taking the year in account
def InterpretNamedDay(dayString):
    namedDayConverstionTable={
        "unknown": (1, 1),
        "unknown ?": (1, 1),
        "new year's day" : (1, 1),
        "edgar allen poe's birthday": (1, 19),
        "edgar allan poe's birthday": (1, 19),
        "groundhog day": (2, 4),
        "canadian national flag day": (2, 15),
        "national flag day": (2, 15),
        "chinese new year": (2, 15),
        "lunar new year": (2, 15),
        "leap day": (2, 29),
        "st urho's day": (3, 16),
        "st. urho's day": (3, 16),
        "saint urho's day": (3, 16),
        "april fool's day" : (4, 1),
        "good friday": (4, 8),
        "easter": (4, 10),
        "national garlic day": (4, 19),
        "world free press day": (5, 3),
        "cinco de mayo": (5, 5),
        "victoria day": (5, 22),
        "world no tobacco day": (5, 31),
        "world environment day": (6, 5),
        "great flood": (6, 19),      # Opuntia, 2013 Calgary floods
        "summer solstice": (6, 21),
        "world wide party": (6, 21),
        "canada day": (7, 1),
        "stampede": (7, 10),
        "stampede rodeo": (7, 10),
        "stampede parade": (7, 10),
        "system administrator appreciation day": (7, 25),
        "apres le deluge": (8, 1),      # Opuntia, 2013 Calgary floods
        "international whale shark day": (8, 30),
        "labor day": (9, 3),
        "labour day": (9, 3),
        "(canadian) thanksgiving": (10, 15),
        "halloween": (10, 31),
        "remembrance day": (11, 11),
        "rememberance day": (11, 11),
        "thanksgiving": (11, 24),
        "before christmas december": (12, 15),
        "saturnalia": (12, 21),
        "winter solstice": (12, 21),
        "christmas": (12, 25),
        "christmas issue": (12, 25),
        "christmas issue december": (12, 25),
        "xmas ish the end of december": (12, 25),
        "boxing day": (12, 26),
        "hogmanay": (12, 31),
        "auld lang syne": (12, 31),
    }
    try:
        return namedDayConverstionTable[dayString.lower()]
    except:
        return None

#-----------------------------------------------------------------------
# Deal with situtions like "late December"
# We replace the vague relative term by a non-vague (albeit unreasonably precise) number
def InterpretRelativeWords(daystring):
    conversionTable={
        "start of": 1,
        "early": 8,
        "early in": 8,
        "mid": 15,
        "middle": 15,
        "?": 15,
        "middle-late": 19,
        "late": 24,
        "end of": 30,
        "the end of": 30,
        "around the end of": 30
    }

    try:
        return conversionTable[daystring.replace(",", " ").replace("-", " ").lower()]
    except:
        return None

#---------------------------------------------------
# Try to make sense of a date string which might be like "10/22/85" or like "October 1984" or just funky randomness
def InterpretDate(dateStr):

    dateStr=dateStr.strip()  # Remove leading and trailing whitespace

    year=None
    month=None
    day=None

    # Some names are of the form "<named day> year" as in "Christmas, 1955" of "Groundhog Day 2001"
    ds=dateStr.replace(",", " ").replace("-", " ").lower().split()  # We ignore hyphens and commas
    if len(ds) > 1:
        year=InterpretYear(ds[len(ds)-1])
        if year != None:        # Fpr this case, the last token must be a year
            dayString=" ".join(ds[:-1])
            dayTuple=InterpretNamedDay(dayString)
            if dayTuple != None:
                return Date(year, dayTuple[0], dayTuple[1])

    # Case: late/early <month> <year>  ("Late October 1999")
    # We recognize this by seeing three or more tokens separated by whitespace, with the first comprising a recognized string, the second-last a month name and the last a year
    ds = dateStr.replace(",", " ").replace("-", " ").lower().split()
    if len(ds) >= 3:
        if len(ds) > 3:                 # If there's more than one early token, recombine just the early tokens.
            temp=" ".join(ds[:-2])
            ds=(temp, ds[len(ds)-2], ds[len(ds)-1])
        day=InterpretRelativeWords(ds[0])

        if day != None:
            month = InterpretMonth(ds[1])
            year = InterpretYear(ds[2])
            if month != None and year != None:
                return Date(year, month, day)

    # Case:  <Month> <year>  ("October 1984", "Jun 73", etc.  Possibly including a comma after the month)
    # We recognize this by seeing two tokens separate by whitespace, with the first a month name and the second a number
    ds=dateStr.replace(",", " ").split()
    if len(ds) == 2:
        month=InterpretMonth(ds[0])
        year=InterpretYear(ds[1])
        if month != None and year != None:
            return Date(year, month, 1)


    # Case:  mm/dd/yy or mm/dd/yyyy
    ds=dateStr.split("/")
    if len(ds) == 3:
        day=InterpretInt(ds[1])
        month=InterpretInt(ds[0])
        year=InterpretInt(ds[2])
        return Date(year, month, day)

    # Case: October 11, 1973 or 11 October 1973
    # We want there to be three tokens, the last one to be a year and one of the first two tokens to be a number and the other to be a month name
    ds=dateStr.replace(",", " ").split()
    if len(ds) == 3:
        year=InterpretYear(ds[2])
        if year != None:
            m0=InterpretMonth(ds[0])
            m1=InterpretMonth(ds[1])
            d0=InterpretInt(ds[0])
            d1=InterpretInt(ds[1])
            if m0 != None and d1 != None:
                return Date(year, m0, d1)
            if m1 != None and d0 != None:
                return Date(year, m1, d0)

    # Case: A 2-digit or 4-digit year by itself
    year=InterpretYear(dateStr)
    if year == None:
        return None
    try:
        return Date(year, 1, 1)
    except:
        return None

#---------------------------------------------------
# Try to make sense of the date information supplied as separate
# Unknown input arguments should be None
def InterpretDayMonthYear(dayStr, monthStr, yearStr):
    import datetime
    import time

    # Let's figure out the date
    year=None
    month=None
    day=None

    if (yearStr != None):
        year = InterpretYear(yearStr)
        if year == None:
            print("   ***Can't interpret year '"+yearStr+"'")
            return None
    if (monthStr != None):
        month = InterpretMonth(monthStr)
        if month == None:
            print("   ***Can't interpret month '" + monthStr + "'")
    if (dayStr != None):
        day = int(dayStr)
        if day == None:
            print("   ***Can't interpret day '" + dayStr + "'")

    if day == None:
        day=1
    if month == None:
        month=1
    return Date(year, month, day)


#-------------------------------------------------------------------
# Find a hyperlink in a strong, returning either the hyperlink or None
def Hyperlink(string):

    # A hyperlink will be of the form <A HREF=["hyperlink"]>...<A>
    lcString=string.lower()
    loc=lcString.find("<a")
    if loc < 0:
        return None

    loc=lcString.find('href="', loc)
    if loc < 0:
        return None

    start=loc+len('href="')
    end=lcString.find('">', start)

    return string[start:end]

#--------------------------------------------------------------------
# Strip the hyperlink stuff from around its display text
def StripHyperlink(text):
    # <A ...HREF=...>display text</A>
    # We'll do this the quick and dirty way and assume that '<' and '>' are not used except in the html
    # If we fail, we just pass the input text back out
    text=text.strip()
    if text == None or len(text) < 8:   # Bail if it's too short to contain a hyperlink
        return text
    if text[0:2].lower() != "<a":       # Bail if it doesn't start with "<A"
        return text
    if text[-4:].lower() != "</a>":     # Bail if it doesn't end with "</A>"
        return text
    loc=text.find(">")      # Find the ">" which ends the opening part of the HTML
    if loc < 0:
        return text

    # OK, it looks like this is a hyperlink.  Strip it away
    text=text[loc+1:-4]

    # Now replace '&nbsp;' with spaces
    return text.replace("&nbsp;", " ")


