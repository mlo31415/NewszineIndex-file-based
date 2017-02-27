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

#---------------------------------------------------------------------
def InterpretYear(yearstring):
    try:
        year=int(yearstring)
    except:
        print("   ***Year conversion failed: '" + yearstring+"'")
        year=None
    return year

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

#---------------------------------------------------
# Try to make sense of the date information
# We'll normally have one of two things:
#       A Date string which might be like "10/22/85" or like "October 1984" or just funky randomness
# Unknown input arguments should be None
def interpretDate(dateStr):
    import datetime
    import time
    import string

    day=None
    month=None
    year=None

    dateStr=dateStr.strip()  # Remove leading and trailing whitespace

    # Case:  <Month> <year>  ("October 1984", "Jun 73", etc.  Possibly including comma after the month)
    # We recognize this by seeing two tokens separate by whitespace, with the first a month name and the second a number
    ds=dateStr.replace(",", " ").split()
    if len(ds) == 2:
        month=InterpretMonth(ds[0])
        year=InterpretYear(ds[1])
        if month != None and year != None:
            return datetime.datetime(year, month, 1).date()

    # Case: late/early <month> <year>  ("Late October 1999")
    # We recognize this by seeing three tokens separate by whitespace, with the first "late", "mid" or "early", the second a month name and the third a number
    ds=dateStr.replace(",", " ").replace("-", " ").split()
    if len(ds) == 3:
        if ds[0].lower() == "early":
            day=8
        if ds[0].lower() == "mid":
            day=15
        if ds[0].lower() == "late":
            day=24
        if day != None:
            month=InterpretMonth(ds[1])
            year=InterpretYear(ds[2])
            if month != None and year != None:
                return datetime.datetime(year, month, day).date()

    # Case:  mm/dd/yy or mm/dd/yyyy
    ds=dateStr.split("/")
    if len(ds) == 3:
        day=int(ds[1])
        month=int(ds[0])
        year=int(ds[2])
        return datetime.datetime(year, month, day).date()

    # Case: October 11, 1973
    ds=dateStr.replace(",", " ").split()
    if len(ds) == 3:
        month=InterpretMonth(ds[0])
        if month != None:
            day=int(ds[1])
            year=int(ds[2])
            return datetime.datetime(year, month, day).date()

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

