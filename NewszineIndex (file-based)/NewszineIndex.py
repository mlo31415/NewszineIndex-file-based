import tkinter
from tkinter import filedialog
import os
import Helpers
import operator
import re

# This is a revision of the LST-file-based NewszineIndex program based on working from a local copy of fanac.org

# Get the directory containing fanac.org
# root = tkinter.Tk()
# root.withdraw()
# lstDirname = filedialog.askdirectory()
# if len(lstDirname) == 0:
#     exit()

# Step 1: Read the newszine data from fanac.org
# For each newszine series:
#       Find its directory
#       Determine the type of index
#       Interpret the index, loading the data into the internal tables
#       The data we want is:
#           Name of newszine series
#           Type (is this a single issue, or a collection of issues?)
#           For each newszine in the series
#               Title
#               Date
#               URL of first page

# Since there's no way to tell a newszine from anything else of fanac.org, we start with a list of newszine series
# Each kind of directory will have a different list

# Lists of newszines with an index.html pointing to a standard table of issues
# (This is the "normal" case)
# Case 1 has the URL and display in the TITLE column
# Case 2 has the URL in a "Headline" column and a displayname in an Issue column
indexHtmlDirectoryList=[("Fanew_Sletter", 1, "title"),
                        ("FanewsCard", 2, None),
                        ("File770", 1, "issue")]

# Out of sheer laziness, I will hardwire the location of the site files.
# Eventually, this should be handled a bit more elegantly.
sitePath="I:/fanac.com backup/_/public/fanzines"

# We shouldn't have to look at more than just the index.html file
for (name, case, stuff) in indexHtmlDirectoryList:
    print("fanzine='"+name+"'")

    # Open the index.html file
    dirpath=os.path.normpath(os.path.join(sitePath, name))
    if not os.path.isdir(dirpath):
        print("    ***Not a directory: '"+dirpath+"'")
        continue
    indexpath=os.path.normpath(os.path.join(dirpath, "index.html"))
    if not os.path.isfile(indexpath):
        print("    ***No index file: '" + indexpath + "'")
        continue
    f=open(indexpath)

    # Read the index file into a string
    contents=f.read()

    # Get the <TITLE>
    (title, loc)=Helpers.FindBracketedText(contents, "TITLE")

    # And find the table
    # We scan the index file for the line "<P><TABLE BORDER="1" CELLPADDING="5">" which begins the table
    locStartTable=contents.lower().find('<p><table border="1" cellpadding="5">')
    if locStartTable == -1:
        print("    ***No table header found")
    contents=contents[locStartTable:]

    # And for </table> which ends the table
    locEndTable=contents.lower().find("</table>")
    if locEndTable == -1:
        print("    ***Table header not terminated")
    contents=contents[:locEndTable]

    # Interpret the table lines

    # The first like of the table should be the header row. Get the column headers.
    # The header row will be bracketed by <TR>, and each header by <TH>.
    (colHeaderRowText, remainder)=Helpers.FindBracketedText(contents, "TR")
    contents=remainder

    # Get the column headers.  They will be bracketed by "<TH>"
    colHeaders=[]
    while True:
        (colHeaderText, remainder)=Helpers.FindBracketedText(colHeaderRowText, "TH")
        if colHeaderText == "" and remainder == "":
            break
        colHeaders.append(Helpers.CannonicizeColumnHeaders(colHeaderText))
        colHeaderRowText = remainder
    print("   Column headers="+str(colHeaders))

    # Now, one by one we read the rows for the individual issues.
    # We want enough information to derive the following:
    #   A URL for the issue
    #   The date of the issue
    #   A title for the issue (Something like "File 770 #23" or "SF Times, January 15, 1953".)
    # This is *very* k/l/u/d/g/y/ tricky since there's no consistency in what information is in the tables: Not content, not order, and not name
    # The first thing we do is drop everything following the </TABLE> tag
    loc=contents.find("</TITLE>")
    if loc != -1:
        contents=contents[:loc]

    # Now loop through the remainder interpreting one row at a time.
    while True:
        # The rows are bounded by <TR>
        (rowText, remainder)=Helpers.FindBracketedText(contents, "TR")
        if rowText == "":
            break;
        contents=remainder

        # Get the cell contents.  They will be bracketed by "<TD>"
        colContents=[]
        while True:
            (cellText, remainder)=Helpers.FindBracketedText(rowText, "TD")
            if cellText == "" and remainder == "":
                break
            colContents.append(cellText)
            rowText = remainder

        #**************************************************************************
        # We're basically setting up a case structure here
        # The problem is that different fanzines have different table structures, and we need to use different means to get the needed data.
        # A case structure is probably the best choice, but since Python doesn't have that, we'll make do with lots of if-then-else clauses.

        # Look for the title and URL, first

        # Case 1:
        if case == 1:
            # The column is supplied in the *stuff* element of
            # The format of the column contents is:
            #  <A stuff HREF="filename.html">displayname</A>
            #       where
            #       stuff is optional misc HTML code (e.g., CLASS-"new")
            #       "filename.html" is the name of the html file
            #       "displayname" is the name as given in the title column of the tabel
            title="title not found"
            loc=Helpers.FindStringInList(colHeaders, stuff)
            if loc != -1:
                title=colContents[loc]
            s=Helpers.DecodeHyperlink(title)

            filename=s[0]
            displayname=s[1]

        elif case == 2:
            # In case 2, the display name is column Issue
            # Column Headline contains the filename as the target of a link
            displayname=None
            loc=Helpers.FindStringInList(colHeaders, "issue")
            if loc == -1:
                print("   ***Missing (case 2) Issue column")
                continue
            displayname=colContents[loc]

            # The Issue column looks like:
            #       <TD CLASS="LEFT"><A HREF="filename">.....</A></TD>
            title = None
            loc = Helpers.FindStringInList(colHeaders, "Headline")
            if loc != -1:
                headline = colContents[loc]
            s=Helpers.DecodeHyperlink(headline)
            if s is None:
                print("   ***Can't (case 2) decode Headline: "+headline)
                continue
            filename=s[0]


        # Now see if we can figure out the date.
        year=None   # We'll detect that a date has been found by year becoming non-Null

        # First, let's see if there's a column named "Date" which we can interpret as a date.
        if year == None:
            loc=Helpers.FindStringInList(colHeaders, "date")
            if loc != -1:
                # We've got a column labeled "date".  Try to interpret it.
                dateText=colContents[loc]
                print("   date="+dateText)

        # If that didn't work, look for columns labelled Year, Month, and Day.
        # Let's figure out the date
        if year == None:
            month=0
            yearCol=Helpers.FindStringInList(colHeaders, "year")
            parseFailure=False
            if (yearCol != -1):
                if yearCol < len(colContents):
                    year = Helpers.InterpretYear(colContents[yearCol])
                else:
                    print("   ***Could not interpret in" + name + ": yearCol=" + str(yearCol) + " colContents='" + str(colContents) + "'")
                    parseFailure = True     # We must have a year

            monthCol=Helpers.FindStringInList(colHeaders, "month")
            if (monthCol != -1):
                if monthCol < len(colContents):
                    month = Helpers.InterpretMonth(colContents[monthCol])
                else:
                    print("***Could not interpret in" + name + ": monthCol=" + str(monthCol) + " colContents='" + str(colContents) + "'")

            dayCol=Helpers.FindStringInList(colHeaders, "day")
            if (dayCol != -1):
                if dayCol < len(colContents):
                    day = Helpers.InterpretDay(colContents[dayCol])
                else:
                    print("***Could not interpret in" + name + ": dayCol=" + str(dayCol) + " colContents='" + str(colContents) + "'")

            if year != None and month == 0:
                month=1 # If a year and no month is specified, we use January
            if year != None and day == 0:
                day=1

        if year == None:
            print("   **** Parse (cases 1 & 2) failure on date")
        i=0
        print("   " + filename + ", " + displayname + "   year=" + str(year) + "   month=" + str(month) + "   day=" + str(day))


    # Start building a fanzine list, containing date, URL and name for each fanzine found
    fanzineList = []



#**************************************************************************************************************
# Old code
#**************************************************************************************************************
# We walk the list of .lst files, analyzing each one.
# The structure of a .lst file is:
# A single line containing the following, semi-colon delimited: Title, Editors, Date range, Zine type
# One or more repetitions of the following
# A blank line
# One or more lines of descriptive material bounded by <P>-</P> or <H3>-</H3>
# A blank line
# A column definition line comprised of a semicolon-delimited list of column headings.  It always begins with "Issue"
# A blank line
# One line for each issue, each comprised of a semicolon-delimited list of data for that fanzine which matches the headings
internalNameDictionary={}
for name in lstList:
    f = open(name)
    #print("\nOpening "+name)
    header = ""
    description = []        # There may be more than one description block, so this is a list of strings
    partialDescription=""   # When we have processed some but not all of the lines in a description, this holds the material found so far
    columnDefs = []         # An array of columdef strings
    while True:
        parseFailure=False
        l = f.readline()
        if len(l) == 0:  # Check for EOF
            break
        if len(l) == 1:  # Ignore blank lines
            continue
        # OK, we have a line with content
        l=l.strip() # Remove leading and trailing whitespace, including the trailing \n
        if len(header) == 0:    # If no header has been processed, then the first non-blank line is the header
            header = l
            #print("Header: "+l)
            internalNameDictionary[os.path.splitext(name)[0].lower()]=header.split(";")[0].strip()
            continue

        # Might this be a Description?  A Description is bounded by <P>-</P> or <H3>-</H3>blocks
        # First look at the case where we're already processing a multi-line description
        if len(partialDescription) > 0:
            partialDescription = partialDescription + " " + l
            if Helpers.RecognizeDescriptionBlockEnd(l):        # Does this line close the multi-line description?
                description.append(partialDescription)
                #print("Description: " + partialDescription)
                partialDescription=""
            continue

        # Might this be a the start of a Description?  A Description is bounded by <P>-</P> or <H3>-</H3> blocks
        if Helpers.RecognizeDescritpionBlockStart(l):
            if Helpers.RecognizeDescriptionBlockEnd(l):        # Does this line also close the description?  (I.e., it's a single-line description.)
                description.append(l)   # This is a single-line description
                #print("Description: " + l)
            else:
                partialDescription=l    # It has <P> or <H3> but no </P> or </H3>, so it's the start of a multi-line description.
            continue

        # Is this the columdef line?
        if len(columnDefs) == 0 and len(l) > 5 and (l[:6].lower() == "issue;" or l[:6].lower() == "title;"):
            columnDefs = l.lower().split(";")               # Split the columndefs line on semicolon
            columnDefs=[c.strip() for c in columnDefs]      # Remove whitespace padding
            columnDefs=[Helpers.CannonicizeColumnHeaders(c) for c in columnDefs]    # Cannonicize headers
            try:
                yearCol = columnDefs.index("year")
            except ValueError:
                yearCol=None
            try:
                monthCol = columnDefs.index("month")
            except ValueError:
                monthCol=None
            try:
                dayCol = columnDefs.index("day")
            except ValueError:
                dayCol=None
            #print("ColumnDef: "+l)
            #print("ColumnDef: YearCol="+str(yearCol)+" MonthCol="+str(monthCol)+" DayCol="+str(dayCol))
            continue

        # OK, it must be a fanzine line
        # We need to analyze it based on the columdefs.
        # Like columndefs, it's a single line of columns separated by semicolons, but in this case we want to preserve case
        fanzineLine = l.split(";")
        fanzineLine=[f.strip() for f in fanzineLine]

        # First, if there isn't a ">" in the first item on the line, we don't actually have the fanzine, so we drop it.
        if fanzineLine[0].find(">") == -1:
            continue

        # Let's figure out the date
        if (yearCol != None):
            if yearCol < len(fanzineLine):
                year=Helpers.InterpretYear(fanzineLine[yearCol])
            else:
                print("   ***FanzineLine too short in "+name+": yearCol="+str(yearCol)+" Fanzineline='"+l+"'")
                parseFailure=True
        if (monthCol != None):
            if monthCol < len(fanzineLine):
                month=Helpers.InterpretMonth(fanzineLine[monthCol])
        else:
            print(   "***FanzineLine too short in"+name+": yearCol=" + str(monthCol) + " Fanzineline='" + l + "'")
            parseFailure = True

        if year == None:
            year=0
            parseFailure = True
        if month == None:
            month=0
            parseFailure = True

        if parseFailure:
            print("File: "+name+"  FanzineDef: " + l+"\n")
            continue
        pattern=re.compile("^([a-zA-Z]*)(.*)>(.*)$")
        m=pattern.match(fanzineLine[0])
        fanzineList.append((year, month, l, name, m.groups()[0], m.groups()[1], m.groups()[2]))
        if m.groups()[0] == None or m.groups()[1] == None or m.groups()[1] == None:
            print("   ***FanzineLine does not have all three RegExs: " + fanzineLine)


# Ok, hopefully we have a list of all the fanzines.  Sort it and print it out
# fanzineList=sorted(fanzineList, key=operator.itemgetter(0, 1))
year=0
month=0
yearCounts={}
for f in fanzineList:
    if f[0] in yearCounts:
        yearCounts[f[0]]=yearCounts[f[0]]+1
    else:
        yearCounts[f[0]]=1
#     line=""
#     if f[0] != year:
#         year=f[0]
#         line=str(year)
#     else:
#         line="    "
#     if f[1] != month:
#         month=f[1]
#         line=line+"  "+str(month)
#     else:
#         line=line+"    "
#     line=line+"  >>"+str(f[2])
#     print(line)

# Now print out the yearCounts data. We turn the dict into a list of tuples and sort it and print it to histogram.txt
histogram=open("./histogram.txt", "w")
yearCountsList=[]
for y in yearCounts:
    yearCountsList.append((y, yearCounts[y]))
yearCountsList=sorted(yearCountsList)
for t in yearCountsList:
    print(str(t[0])+": "+str(t[1]), file=histogram)
histogram.close()

# Now create the html
# The directories containing the scans are expected to be in a sibling directory called "fanzines"
fanzinesDirname=os.path.normpath(os.path.join(lstDirname, "../fanzines"))

# Get a list of all the directories in fanzines
os.chdir(fanzinesDirname)
dirlist = os.listdir(".")
dirlist = [f for f in dirlist if os.path.isdir(f)]

# OK.  Now we need to determine the directory name for each LST file.
# This is non-trivial.
# For each LST file:
#   Each LST file contains a header line with semicolon-delimited information in it.  The first field is the internal name of the fanzine.
#   We first check to see if there is a directory present matching the internal name (with all blanks replaced by '_')
#   If not, we check to see if there is a directory present matching the LST file's name.
#   If not, we check to see if there is an entry in the dirnameExceptions dictionary.
dirnameExceptions={
    # LST name : Directory name
    # the LST name is case-insensitive
    "blooming" : "Bloomington_News",
    "bullshe1" : "Bullsheet",
    "bullshe2" : "Bullsheet",
    "fanewscard" : "FanewsCard",
    "fantasy_news_newseries" : "Fantasy_News_NewSeries",
    "file" : "File770",
    "luna" : "Luna",
    "midwest" : "MidWest_Fan_News",
    "neosfs" : "NEOSFS",
    "qx" : "QX",
    "sfchron" : "SF_Chronicle",
    "sfnews" : "SF_News",
    "sfnewsco" : "SF_Newscope",
    "sfnl-rw" : "SFNL-RichardWilson",
    "sftimes-ger" : "SFTimes_German",
    "sfweekly" : "SFWeekly",
    "sweetness" : "Sweetness_Light"}

# Convert the values of the internalNameDictionary to directory form (spaces -> '_')
for d in internalNameDictionary:
    internalNameDictionary[d]=internalNameDictionary[d].replace(" ", "_")

lstNameToDirNameMap={}
for file in lstList:
    file=os.path.splitext(file)[0]
    dirname=None
    if internalNameDictionary[file.lower()] in dirlist:
        dirname=internalNameDictionary[file.lower()]
    else:
        if file in dirlist:
            dirname=file
        else:
            if file.lower() in dirnameExceptions:
                dirname=dirnameExceptions[file.lower()]

    if dirname == None:
        print("   ***'" + file + "' seems to have no matching directory")
    lstNameToDirNameMap[file]=dirname

# for d in lstNameToDirNameMap:
#    print(d+" --> "+lstNameToDirNameMap[d]+"    "+str(len(os.listdir(lstNameToDirNameMap[d]))))


months={1 : "January",
        2 : "February",
        3 : "March",
        4 : "April",
        5 : "May",
        6 : "June",
        7 : "July",
        8 : "August",
        9 : "September",
        10 : "October",
        11 : "November",
        12 : "December"}

filePrefix={    # This deals with the arbitrary fanzine prefixes used on the website
    # The key for each pair is the directory name, the value is the file prefix used in the directories
    "Ansible" : "Ansible",
    "Australian_SF_News" : "auss",
    "Axe" : "Axe",
    "Barsoomian_Times" : "Barsoomian_Times",
    "Bay_Area_News" : "Bay_Area",
    "Bloomington_News" : "Bloomington_News",
    "Bullsheet" : "Bullsheet",
    "FANAC" : "FANAC",
    "FanewsCard" : "Fanews",
    "Fanew_Sletter" : "Fanew_Sletter",
    "Fantasy_Fiction_Field" : "FanFic_Field",
    "Fantasy_News" : "Fantasy_News",
    "Fantasy_News_NewSeries" : "fn",
    "Fantasy_Times" : "Fantasy_Times",
    "FFF" : "FanFic_Field",
    "Fiawol" : "Fiawol",
    "File770" : "File770",
    "Focal_Point" : "Focal_Point",
    "Futurian_Observer" : "Futurian_Observer",
    "Karass" : "Karass",
    "Luna" : "Luna",
    "MidWest_Fan_News" : "MidWest_Fan_News",
    "Nebula" : "Nebula",
    "NEOSFS" : "NEOSFS",
    "Newfangles" : "Newfangles",
    "Norstrilian_News" : "Norstrilian_News",
    "Organlegger" : "Organlegger",
    "Phan" : "Phan",
    "QX" : "QX",
    "Rally" : "Rally",
    "Ratatosk" : "Ratatosk",
    "Sanders" : "Sanders",
    "Science_Fantasy_Review" : "scif",
    "Science_Fiction_Newsletter" : "SFNews",
    "Science_Fiction_Times" : "Science_Fiction_Times",
    "Scream" : "Scream",
    "SF_News" : "SF_News",
    "SF_Newscope" : "sfn",
    "SF_Chronicle" : "sfc",
    "SFinctor" : "SFinctor",
    "SFNL-RichardWilson" : "SFNL",
    "SFTimes_German" : "SFTimes_German",
    "SFWeekly" : "SFWeekly",
    "Shards_of_Babel" : "Shards_of_Babel",
    "Skyrack" : "Skyrack",
    "Spang_Blah" : "Spang_Blah",
    "SpinDizzy" : "SpinDizzy",
    "Starspinkle" : "Starspinkle",
    "STEFCARD" : "STEFCARD",
    "Swefanac" : "Swefanac",
    "Sweetness_Light" : "Sweetness_Light",
    "Sylmarillion" : "Sylmaril",
    "Thyme" : "Thyme",
    "Tympany" : "Tympany",
    "Winnie" : "Winnie"
}

f=open("../newszinestable.txt", "w")
print('<table border="2">', file=f) # Begin the main table

fanzineList=sorted(fanzineList, key=operator.itemgetter(0, 1))
monthYear=""
for fmz in fanzineList:

    # This section deals with complicated and sometimes problematic data, so we do a bit of trial and error

    url=lstNameToDirNameMap[os.path.splitext(fmz[3])[0]]        # Directory name
    try:
        filePrefix[url]     # We need to make sure that this fanzine is in the filePrefix table.
    except:
        print("   *** '"+str(url)+"' is missing from the filePrefix table")
        print("        fmz="+str(fmz))
        continue

    # The file on disk can be a pdf or an html file.  If it's a pdf, it will already have a pdf extension
    url = url + "/" + filePrefix[url] + fmz[5]
    if url[-4:].lower() !=  ".pdf": # If it's not already got a .pdf extension, add an .html extension
        url=url+".html"

    if not os.path.isfile(url):
        print("   *** File does not exist: "+url)
        continue

    # Start the row
    # Put the month & year in the first column of the table only if it changes.
    newMothYear=str(months[fmz[1]])+" "+str(fmz[0])
    if newMothYear != monthYear:
        if monthYear != "":   # Is this the first month box?
            print('</table></td></tr>', file=f)  # No.  So end the previous month box

        print('<tr><td><table border="0">', file=f)    # Start a new month box
        monthYear=newMothYear
        print('    <tr><td width="120">' + newMothYear + '</td>', file=f)
    else:
        print('    <tr><td width="120">&nbsp;</td>', file=f)        # Add an empty month box

    # The hyperlink goes in column 2
    print('        <td width="250">' + '<a href="./'+url+'">'+fmz[6]+'</a>' + '</td>', file=f)

    # And end the row
    print('  </tr>', file=f)

print("</table></td></tr>", file=f)
print('</table>', file=f)
f.close()


pass