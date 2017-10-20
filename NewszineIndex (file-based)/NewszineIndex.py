import tkinter
from tkinter import filedialog
import os
import Helpers
import operator
import re
from datetime import datetime

# This is a revision of the LST-file-based NewszineIndex program based on working from a local copy of fanac.org

# Get the directory containing fanac.org
# root = tkinter.Tk()
# root.withdraw()
# lstDirname = filedialog.askdirectory()
# if len(lstDirname) == 0:
#     exit()

# The object is to build a fanzine list, containing date, URL and name for each fanzine found
fanzineList = []

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

# The following table lists the newszines to process. For each newszine, there are four pieces of information:
# 1: The name of the directory within /fanzines/ in which to look for index.html
# 2: A case which specifies the structure of the index.html file
#   Case 1 has the URL and display in the TITLE column
#   Case 2 has the URL in a "Headline" column and a displayname in an Issue column
# 3: The site is inconsistent about the title of the column used by case 1 (the most common case by far). This specifies the name of the column to look in.
# 4: When the file containing the table is not named index.html, this is the name of the file to look in.
indexHtmlDirectoryList=[("Ansible", 1, "issue", None),
                        ("Australian_SF_News", 1, "issue", None),
                        ("Australian_SF_Newsletter", 1, "issue", None),
                        ("Axe", 1, "title", None),
                        ("Barsoomian_Times", 1, "issue", None),
                        ("Bloomington_News", 1, "title", None),
                        ("Bullsheet", 1, "title", "Bullsheet1-00.html"),
                        ("Bullsheet", 1, "title", "Bullsheet2-00.html"),
                        ("CHAT", 1, "issue", None),
                        ("Chronicle", 1, "issue", None),
                        ("Convention", 1, "issue", None),
                        ("Fanew_Sletter", 1, "title", None),
                        ("FanewsCard", 2, None, None),
                        ("FanParade", 1, "issue", None),
                        ("FANAC", 1, "issue", None),
                        ("FANAC_Updates", 1, "issue", None),
                        ("Fantasy_News", 1, "issue", None),
                        ("Fantasy_News_NewSeries", 1, "issue", None),
                        ("Fantasy_Newsletter", 1, "issue", None),
                        ("Fantasy_Times", 1, "issue", None),
                        ("FFF", 1, "issue", None),
                        ("Fiawol", 1, "issue", None),
                        ("FightingSmofs", 1, "issue", None),
                        ("File770", 1, "issue", None),
                        ("Focal_Point", 1, "issue", None),
                        ("Futurian_Observer", 1, "title", None),
                        ("Karass", 1, "issue", None),
                        ("Luna", 1, "issue", None),
                        ("Midwest_Fan_news", 1, "issue", None),
                        ("Nebula", 1, "issue", None),
                        ("NEOSFS", 1, "issue", None),
                        ("Newfangles", 1, "issue", None),
                        ("Norstrilian_News", 1, "issue", None),
                        ("Organlegger", 1, "issue", None),
                        ("Phan", 1, "issue", None),
                        ("QX", 2, None, None),
                        ("Rally", 1, "issue", None),
                        ("Ratatosk", 1, "issue", None),
                        ("Sanders", 1, "issue", None),
                        ("Sat_Morning_Gazette", 1, "issue", None),
                        ("Science_Fantasy_Review", 1, "issue", None),
                        ("Science_Fantasy_News", 1, "issue", None),
                        ("Science_Fiction_Newsletter", 1, "title", None),
                        ("Scream", 1, "issue", None),
                        ("STEFCARD", 2, None, None),
                        ("SF_Chronicle", 1, "issue", None),
                        ("SF_News", 1, "issue", None),
                        ("SF_Newscope", 1, "title", None),
                        ("SFinctor", 1, "issue", None),
                        ("SFTimes_German", 1, "issue", None),
                        ("SFWeekly", 1, "issue", None),
                        ("SFWorld", 1, "issue", None),
                        ("Skyrack", 1, "issue", None),
                        ("Shards_of_Babel", 1, "issue", None),
                        ("Spang_Blah", 1, "issue", None),
                        ("SpinDizzy", 1, "issue", None),
                        ("Starspinkle", 1, "title", None),
                        ("STEFNEWS", 1, "issue", None),
                        ("Sweetness_Light", 1, "issue", None),
                        ("Swefanac", "issue", 1, None),
                        ("Sydney_Futurian",  1, "issue", None),
                        ("Sylmarillion", 1, "issue", None),
                        ("Thyme", 1, "issue", None),
                        ("Tympany",  1, "issue", None)]


# Out of sheer laziness, I will hardwire the location of the site files.
# Eventually, this should be handled a bit more elegantly.
sitePath="I:/fanac.com backup/_/public/fanzines"

# We shouldn't have to look at more than just the index.html file
for (name, case, stuff, tableSource) in indexHtmlDirectoryList:
    print("fanzine='"+name+"'")

    # Open the index.html file
    dirpath=os.path.normpath(os.path.join(sitePath, name))
    if not os.path.isdir(dirpath):
        print("    ***Not a directory: '"+dirpath+"'")
        continue
    tableFileName="index.html"
    if tableSource != None:
        tableFileName=tableSource
    indexpath=os.path.normpath(os.path.join(dirpath, tableFileName))
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
    # This is *very* k/l/u/d/g/y/ tricky since there's not much consistency in what information is in the tables: Not content, not order, and not name
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
        rowTextCopy=rowText # We keep a copy for use in error messages, since rowText itself gets nibbled away as it is being processed.

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

            if s == None or s[0] == None  or s[1] == None:
                print("   ***Could not decode HREF in field '"+stuff+"';  contents='"+title+"'")
                continue

            filename=s[0]
            displayname=s[1]

        elif case == 2:
            # In case 2, the display name is column Issue
            # Column Headline contains the filename as the target of a link
            displayname=None
            loc=Helpers.FindStringInList(colHeaders, "issue")
            if loc == -1:
                print("   ***"+rowTextCopy)
                print("   ***Missing Issue column (case 2)")
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
                print("   ***"+rowTextCopy)
                print("   ***Can't decode Headline (case 2): "+headline)
                continue
            filename=s[0]


        # Now see if we can figure out the date.
        year=0   # We'll detect that a date has been found by year becoming non-zero
        month=0
        day=0

        # First, let's see if there's a column named "Date" which we can interpret as a date.
        if year == 0:
            loc=Helpers.FindStringInList(colHeaders, "date")
            if loc != -1:
                # We've got a column labeled "date".  Try to interpret it.
                dateText=colContents[loc]
                d=Helpers.InterpretDateString(dateText)
                if d is not None:
                    year=d.year
                    month=d.month
                    day=d.day

        # If that didn't work, look for columns labelled Year, Month, and Day.
        # Let's figure out the date
        if year == 0:
            month=0
            yearCol=Helpers.FindStringInList(colHeaders, "year")
            parseFailure=False
            if (yearCol != -1):
                if yearCol < len(colContents):
                    year = Helpers.InterpretYear(colContents[yearCol])
                else:
                    print("   ***" + rowTextCopy)
                    print("   ***Could not interpret in" + name + ": yearCol=" + str(yearCol) + " colContents='" + str(colContents) + "'")
                    parseFailure = True     # We must have a year

            monthCol=Helpers.FindStringInList(colHeaders, "month")
            if (monthCol != -1):
                if monthCol < len(colContents):
                    month = Helpers.InterpretMonth(colContents[monthCol])
                else:
                    print("   ***" + rowTextCopy)
                    print("***Could not interpret in" + name + ": monthCol=" + str(monthCol) + " colContents='" + str(colContents) + "'")

            dayCol=Helpers.FindStringInList(colHeaders, "day")
            if (dayCol != -1):
                if dayCol < len(colContents):
                    day = Helpers.InterpretDay(colContents[dayCol])
                else:
                    print("   ***" + rowTextCopy)
                    print("***Could not interpret in" + name + ": dayCol=" + str(dayCol) + " colContents='" + str(colContents) + "'")

            if year != None and month == 0:
                month=1 # If a year and no month is specified, we use January
            if year != None and day == 0:
                day=1

        if year == 0:
            print("   ***" + rowTextCopy)
            print("   **** Parse failure on date (cases 1 & 2)")
        i=0
#        print("   " + filename + ", " + displayname + "   year=" + str(year) + "   month=" + str(month) + "   day=" + str(day))

        fanzineList.append(year, month, day, displayname, filename)


#******************************************************************************************
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
#fanzinesDirname=os.path.normpath(os.path.join("something", "../fanzines"))
fanzineDirname=sitePath


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