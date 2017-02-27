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

def InterpretYear(yearstring):
    try:
        year=int(yearstring)
    except:
        print("   ***Year conversion failed: '" + yearstring+"'")
        year=None
    return year

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

#---------------------------------------------------
# Try to make sense of the date information
# We'll normally have one of two things:
#       A month and a year as separate strings
#       A Date string which might be like "10/22/85" or like "October 1984" or just funky randomness
# Unknown input arguments should be None
def interpretDate(dateStr, monthStr, yearStr):
    import datetime

    # Let's figure out the date
    parseFailure=False      # parseFailure gets set to True when there's a string which can't be interpreted
    year=None
    month=None
    day=None

    if (yearStr != None):
        year = InterpretYear(yearStr)
        if year == None:
            print("   ***Can't interpret year '"+yearStr+"'")
            parseFailure = True
    if (monthStr != None):
        month = Helpers.InterpretMonth(monthStr)
        if month == None:
            print("   ***Can't interpret month '" + monthStr + "'")
            parseFailure = True

    if year != None and month != None:
        return datetime.datetime(year, month, 1)
    if year != None:
        return datetime.datetime(year, 1, 1)


    if dateStr != None:
        # Try to interpret the date string
        date=datetime.strptime(dateStr, "%d/%b/%y")
        return date

    return None


