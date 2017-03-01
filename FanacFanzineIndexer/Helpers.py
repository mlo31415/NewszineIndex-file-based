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

# ---------------------------------------------------------------------
def InterpretInt(intstring):
    try:
        return int(intstring)
    except:
        return None

#---------------------------------------------------------------------
def InterpretYear(yearstring):
    if len(yearstring) != 2 and len(yearstring) != 4:
        return None

    return InterpretInt(yearstring)

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
# Returns a month/day tuple
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
        "summer solstice": (6,21),
        "canada day": (7, 1),
        "stampede": (7, 10),
        "stampede rodeo": (7, 10),
        "stampede parade": (7, 10),
        "system administrator appreciation day": (7, 25),
        "international whale shark day": (8, 30),
        "labor day": (9, 3),
        "labour day": (9, 3),
        "(canadian) thanksgiving": (10, 15),
        "halloween": (10, 31),
        "remembrance day": (11, 11),
        "rememberance day": (11, 11),
        "thanksgiving": (11, 24),
        "saturnalia": (12, 21),
        "christmas": (12, 25),
        "christmas issue": (12, 25),
        "boxing day": (12, 26),
        "hogmanay": (12, 31),
        "auld lang syne": (12, 31),
    }
    try:
        return namedDayConverstionTable[dayString.lower()]
    except:
        return None

def InterpretRaletiveWords(daystring):
    conversionTable={
        "early": 8,
        "early in": 8,
        "mid": 15,
        "middle": 15,
        "middle-late": 19,
        "late": 24,
        "end of": 28,
        "the end of": 28,
        "around the end of": 28
    }

#---------------------------------------------------
# Try to make sense of a date string which might be like "10/22/85" or like "October 1984" or just funky randomness
def interpretDate(dateStr):
    import datetime

    dateStr=dateStr.strip()  # Remove leading and trailing whitespace

    year=None
    month=None
    day=None

    # Some names are of the form "<named day> year" as in "Christmas, 1955" of "Groundhog Day 2001"
    ds=dateStr.replace(",", " ").replace("-", " ").lower().split()  # We ignore hyphens and commans
    if len(ds) > 1:
        year=InterpretYear(ds[len(ds)-1])
        if year != None:        # Fpr this case, the last token must be a year
            dayString=" ".join(ds[:-1])
            dayTuple=InterpretNamedDay(dayString)
            if dayTuple != None:
                return datetime.datetime(year, dayTuple[0], dayTuple[1]).date()

    # Case: late/early <month> <year>  ("Late October 1999")
    # We recognize this by seeing three or more tokens separated by whitespace, with the first comprising a recognized string, the second-last a month name and the last a year
    ds = dateStr.replace(",", " ").replace("-", " ").lower().split()
    if len(ds) >= 3:
        if len(ds) > 3:                 # If there's more than one early token, recombine just the early tokens.
            temp=" ".join(ds[:-2])
            ds=(temp, ds[len(ds)-2], ds[len(ds)-1])
        if ds[0] == "early":
            day = 8
        if ds[0] == "early in":
            day = 8
        if ds[0] == "mid":
            day = 15
        if ds[0] == "middle":
            day = 15
        if ds[0] == "late":
            day = 24
        if ds[0] == "end of":
            day=28
        if ds[0] == "around the end of":
            day=28

        if day != None:
            month = InterpretMonth(ds[1])
            year = InterpretYear(ds[2])
            if month != None and year != None:
                return datetime.datetime(year, month, day).date()

    # Case:  <Month> <year>  ("October 1984", "Jun 73", etc.  Possibly including a comma after the month)
    # We recognize this by seeing two tokens separate by whitespace, with the first a month name and the second a number
    ds=dateStr.replace(",", " ").split()
    if len(ds) == 2:
        month=InterpretMonth(ds[0])
        year=InterpretYear(ds[1])
        if month != None and year != None:
            return datetime.datetime(year, month, 1).date()


    # Case:  mm/dd/yy or mm/dd/yyyy
    ds=dateStr.split("/")
    if len(ds) == 3:
        day=InterpretInt(ds[1])
        month=InterpretInt(ds[0])
        year=InterpretInt(ds[2])
        return datetime.datetime(year, month, day).date()

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
                return datetime.datetime(year, m0, d1).date()
            if m1 != None and d0 != None:
                return datetime.datetime(year, m1, d0).date()

    # Case: A 4-digit year by itself
    if len(dateStr) == 4:
        year=InterpretYear(dateStr)
        if year == None:
            return None
        try:
            return datetime.datetime(year, 1, 1).date()
        except:
            return None

#---------------------------------------------------
# Try to make sense of the date information supplied as separate
# Unknown input arguments should be None
def interpretDayMonthYear(dayStr, monthStr, yearStr):
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
    return datetime.datetime(year, month, day).date()


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

