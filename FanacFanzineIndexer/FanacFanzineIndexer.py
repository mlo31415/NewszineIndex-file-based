import tkinter
from tkinter import filedialog
import os
import Helpers
import collections
import re

# Get the directory containing the copy of the fanac.org website to be analyzed.
root = tkinter.Tk()
root.withdraw()
dirname = filedialog.askdirectory()
if len(dirname) == 0:
    exit()

# The directory structure is <stuff>\public\fanzines
# This directors contains one directory per fanzine
# Each fanzine directory contains an HTML file index.html and the files it refers to
# There are several structures/formats for a fanzine directory

# *** Each fanzine is a PDF
#       The index.html file contains a table, and each row points to a pdf file

# *** The fanzines are individual image files of a page
#       The index.html file contains a table, and each row points to an HTML file which is a frame hosting the image
#       The frame also has buttons to go to the next page and to the previous page. These bring up the frame page of the next or previous page.

# The strategy here is to walk the entire fanzines directory and build up the structure of the entire directory before doing any processing.

# Some directory formats are hard to recognize and/or archaic. They are listed by hand, here.
singleIssueDirectories=["Abstract", "Chanticleer", "Constellation", "Entropy", "Fan-Fare", "FanToSee", "Leaflet", "LeeHoffman",
                        "Mallophagan", "Masque", "Monster", "NewFrontiers", "NOSFAn", "Planeteer", "Sense_of_FAPA",
                        "SF_Digest", "SF_Digest_2", "SFSFS", "SpaceDiversions", "SpaceFlight", "SpaceMagazine",
                        "Starlight", "SunSpots", "Tomorrow", "Vanations", "Vertigo", "WildHair", "Willis_Papers", "X", "Yandro"]

# These simply lack the needed data
hopelessDirectories=["BNF_of_IZ", "Enchanted_Duplicator"]

# These have index pages which are missing the top title block
missingTopTitleBlock=["BestOfSusanWood"]

# And these are directories under fanzines that are weird in some way.  In most cases, they;re not fanzines but convention publications
nonStandardDirectories={"AngeliqueTrouvere", "AvramDavidson", "Beyond the Enchanted Duplicator to the Enchanted Convention",
                        "Bids_etc", "Boskone", "Bullsheet", "Chicon", "Cinvention", "Clevention",
                        "ConStellation", "Cosmag", "Denvention", "Don_Ford_Notebook", "Eastercon", "Gegenschein",
                        "Gotterdammerung", "Helios", "IGOTS", "IguanaCon", "Interaction", "LASFS", "Loncon", "Lunacon",
                        "MagiCon", "Mimosa", "Minicon", "Miscellaneous", "Monster", "NebulaAwardsBanquet", "NEOSFS",
                        "Nolacon", "NOLAzine", "NorWesCon", "Novae_Terrae", "NYcon", "OKon", "Pacificon", "Philcon", "Pittcon",
                        "Plokta", "Seacon", "SFCon", "sfnews", "Solacon", "Syllabus", "Tropicon", "Wrevenge", "Yokohama"}

# Get a list of all the directories in the directory.
dirList = [f for f in os.listdir(dirname) if os.path.isdir(os.path.join(dirname, f))]

#=================================
#  Step 1

# Walk the list of directories and create fanzines
# fanzines is a dictionary (indexed by name) with each element being tuple consisting of the directory name and the index table
fanzines={}

for directory in dirList:
    if directory in singleIssueDirectories:
        print(directory + "  (single-issue -- skipped)")
        continue
    if directory in hopelessDirectories:
        print(directory + "  (hopeless -- skipped)")
        continue
    if directory in nonStandardDirectories:
        print(directory + "  (non-standard -- skipped)")
        continue
    print(directory + " ...processing")

    # There should be an index.html file.  Open it.
    indexfilename=os.path.join(dirname, directory, "index.html")
    if not os.path.isfile(indexfilename):
        print("******Missing: "+indexfilename+"   ...Aborting.")
        continue

    # The most common directory index.html format
    # <title></title> tagging the fanzine's display name
    # Some page info in <h2></h2>
    #   (Sometimes some untagged bumpf following this.)
    # A top table which holds the top navigation buttons and can be ignored. (This is missing in a few directories.)
    # A middle table which holds the rows of issue links.
    # A bottom table holds the bottom navigation buttons and can be ignored, also.
    # Some more untagged bumpf included who scanned it and the update date.

    # Read the index.html file.
    with open(indexfilename, "r") as file:
        contents=file.read()

    # Get the <title>
    t=Helpers.ExtractTaggedStuff(contents, 0, "title")
    if t is None:
        print("******Could not find <title>...</title>.  Aborting.")
        continue
    title=t[0]
    loc=t[1]

    # Try to find the first two tables
    if directory not in missingTopTitleBlock:
        t=Helpers.ExtractTaggedStuff(contents, loc, "table")    # Ignored first table
        if t is None:
            print("******Could not find first <table>.  Aborting.")
            continue
        loc=t[1]

    t=Helpers.ExtractTaggedStuff(contents, loc, "table")
    if t is None:
        print("******Could not find second <table>.  Aborting.")
        continue
    tableText=t[0]

    # Eliminate <p> and </p>.  The former because they are usually not closed by a </p> and the latter because sometimes they are.
    tableText=tableText.replace("<p>", "").replace("<P>", "").replace("</p>", "").replace("</P>", "")
    # Eliminate /n
    tableText=tableText.replace("\n", "")

    # OK, start decoding the index table.

    # The first row (bounded by <tr> tags) should be column headers bounded by <th> tags.
    # We will loop until we run out of <th> tags
    columns=[]
    t=Helpers.ExtractTaggedStuff(tableText, 0, "tr")
    if t is None:
        print("******Could not find column headers row.  Aborting.")
        continue
    headers=t[0]
    endheaders=t[1]
    loc=0
    while True:
        t=Helpers.ExtractTaggedStuff(headers, loc, "th")
        if t is None:
            break
        columns.append(t[0])
        loc=t[1]

    print("   "+str(columns))

    # Create the index table
    # It is a list of rows, with the first row being the header row
    # Each row is a list of columns, so that a table is a 2-dimensional array stored as a list of lists
    columns.append("Hyperlink")     # Add a Hylerlink column
    table=[columns]                 # And add the header row to the table
    # OK. Now we decode the data rows.  There should be one cell for each header column in each row.  The rows will be saved as a list of tuples.
    loc=endheaders
    hyper=""    # This will hold any hyperlink encountered in the parsing
    while True:     # Loop over rows
        row=()
        t=Helpers.ExtractTaggedStuff(tableText, loc, "tr")  # Extract the whole row
        if t is None:
            break
        rowText=t[0]
        endrow=t[1]

        loc=0
        while True:     # Loop over the row, extracting the columns in turn
            t = Helpers.ExtractTaggedStuff(rowText, loc, "td")
            if t is None:
                break
            h=Helpers.SeparateHyperlink(t[0])      # See if there's a hyperlink in this cell.  If so, remove the html, leaving the display text in the cell.  Save the hyperlink's URL to go in the new last column
            if h is not None:
                t=(h[1], t[1])
                hyper=h[0]
                h=None
            row += t[0],
            loc = t[1]
        loc=endrow

        row += hyper,        # Add the hyperlink column.  It may be an empty string.

        table.append(row)

    # Create the tuple consisting of the directory name and the index table and store it as a dictionary entry under the fanzine's name
    fanzines[title]=(directory, table)

#=================================
# Step 2

# OK, now we've inhaled the structure of the fanzines part of the website.  Time to make sense of it
# Unfortunately, the website is pretty sloppy and uses different headings on different pages for the same data, so we need to deal with that
# Here is the tables of synomyms for columns we actually use
columnSynonyms={
    "Month" : "Month",
    "Mo." : "Month",
    "Quarter/Month" : "Month",
    "Season" : "Month",
    "Issue" : "Issue",
    "Fanzine" : "Issue",
    "#" : "Number",
    "Num" : "Number",
    "Number": "Number",
    "No" : "Number",
    "No," : "Number",
    "Year" : "Year",
    "Volume" : "Volume",
    "Vol" : "Volume",
    "Vol." : "Volume",
    "Vol/#" : "Vol/#",
    "Vol./#" : "Vol/#",
    "Title" : "Title",
    "Day" : "Day",
    "Date" : "Date",
    "Issue Date" : "Date",
    "Published": "Date",
    "Hyperlink": "Hyperlink"
}

# We want to make sure we catch all the useful data, so we also have a list of columns we will ignore.
ignoreColumns=["Headline", "Pages", "Notes", "Type", "PDF Size", "Description", "Country", "Editor/Publisher", "Contains", "Editor", "Editors", "Date, Notes",
               "Editor/s", "Author/Artist", "Repro", "Publication", "Pp.", "PoB", "LGP", "GP", "Size", "Publisher", "Publishers", "Fanzine", "APA", "Page", "Zine",
               "Author", "Art by", "Story by", "Type of Material", "Reprinted from:", "Content", "Sub-Title"]

# For each issue, we want the following:
#   Date
#   Issue title (Vol/Num or just Num)
#   HTML link

# The data will be stored in a new dictionary with the same structure as "fanzines"
# The keys will be the fanzine title
# The value will be a list of namedtuples of (date, issue, hyperlink)
standardizedFanzines={}
IssueData=collections.namedtuple("IssueData", ["date", "title", "hyperlink", "directory"])   # Create the factory for the Issue Data named tuple

# Walk the fanzines dictionary and extract the data to create the standardized version
for title in fanzines:
    table=fanzines[title][1]    # We want just the index table
    directory=fanzines[title][0]
    firstTime=True
    columnHeaders=[]
    for tableRow in table:
        if firstTime:
            # The first item in the table is the column headers, but we need to convert these to their standard forms
            for header in tableRow:
                if header in ignoreColumns:
                    columnHeaders.append("ignored")
                else:
                    if header in columnSynonyms:
                        columnHeaders.append(columnSynonyms[header])
                    else:
                        print("******"+title+": Column header not recognized:  "+header)
                        columnHeaders.append("not recognized")
            firstTime=False
            continue

        # The rest of the rows are data rows.

        # The next step is to try to make sense of the date information and to generate a date for each issue.
        # First see if there's a date field
        date=None
        try:
            dateField=tableRow[columnHeaders.index("Date")]
            date=Helpers.InterpretDate(dateField)
            if date is None:
                print("******"+title+": date interpretation failed, date=" + dateField)
        except ValueError:
            date=None

        # If the date field didn't work out(either because there was none or because it was uninterpretable), see if there are individual month, day and year fields.
        if date is None:
            try:
                yearField=tableRow[columnHeaders.index("Year")]
                year=Helpers.InterpretYear(yearField)
            except:
                year=None

            try:
                monthField=tableRow[columnHeaders.index("Month")]
                month=Helpers.InterpretMonth(monthField)
            except:
                month=None

            if month is None:
                month=1     # If there's no readable month, assume we have a year only and date it January

            try:
                dayField=tableRow[columnHeaders.index("Day")]
                day=int(dayField)
            except:
                day=None

            if day is None:
                day=1       # If there's no readable day, assume we have a year and month only and date it the 1st

            if year is not None:    # We must have a year.
                try:
                    date=Helpers.Date(year, month, day)
                except:
                    print("******BAD DATE. Title= " + title + "   year=" + str(year)+"  month="+str(month)+"   day="+str(day))
                    date=None

        if date is None:
            print("******NO DATE FOUND. Title= "+title+ "   Table row="+" ".join(tableRow))
            continue

        # Next we find (or construct) the issue title
        # Sometimes there's an issue title, sometimes there isn't. (The data's a real mess!)
        # Worse, sometimes "Issue" is an issue number
        # Examples:
            # "<title> <n>" in column "Title"  (<n> is some sort of unique issue designator)  There is no column "Issue"
            #       Starspinkle, Speculation, Skyrack, VOID
            # "<title> <n>" in column "Issue"  (<n> is some sort of unique issue designator) There is no column "Title".
            #       Winnie, Voice of the Imagi-Nation, Vega, Tympany, Tightbeam, Sylmarillion, The Sydney Futurian, Swefanac, Spang Blah, Spaceship, Skyhack, Shangri-LA, SF
            #       SFinctor, SF Weekly, SF Times Germany, Scream, Scientifantasy, "Science, Fantasy, and Science Fiction", Science Fiction News (Australia), Science Fiction Newscope
            # No title column, but Issue, Month, Day, Year columns exist
            #       STEFcard
            # Title column exists, but contains series title rather than issue title.  Issue, Month, Day, Year columns exist
            #       Wastebasket, Vampire, Toto, Slant, Science Fiction Newsletter
            # Fanzine column exists, but contains series title rather than issue title.  Issue, Month, Day, Year columns exist
            #       Spacewarp
            #  Inconsistant
            #       Spaceways

        # We can deal with some of these, anyway.
        # We'll start by scanning the column headers looking for "title" and "issue"
        indexIssue=Helpers.GetIndex(columnHeaders, "Issue")
        indexTitle=Helpers.GetIndex(columnHeaders, "Title")

        issueTitle=None
        if indexIssue is not None and indexTitle is None:
            issueTitle=tableRow[indexIssue]
        elif indexIssue is None and indexTitle is not None:
            issueTitle=tableRow[indexTitle]
        elif indexIssue is not None and indexTitle is not None:
            # For now we'll use Title, but this may need to be improved
            issueTitle=tableRow[indexTitle]

        # Because the site is so inconsistent, sometimes the issue name doesn't have an issue or volume number
        # In that case, we can't use it and must try to construct one.
        pattern=re.compile("[0-9]")
        betterOneFound = None
        if issueTitle is not None and not re.search(pattern, issueTitle):
            # Case: There is a column "Vol/#"
            if betterOneFound is None:
                indexVolNo=Helpers.GetIndex(columnHeaders, "Vol/#")
                if indexVolNo is not None:
                    betterOneFound=title+" "+tableRow[indexVolNo]

            # Case: There is a "Number" column
            if betterOneFound is None:
                indexNum=Helpers.GetIndex(columnHeaders, "Number")
                if indexNum is not None:
                    betterOneFound=title+" "+tableRow[indexNum]

        if betterOneFound is not None:
            issueTitle=betterOneFound

        # MT Void is a special case since there are so many of them, none of which have the fanzine *name* in the title!
        if title == "The MT Void":
            issueTitle="The MT Void "+issueTitle.replace("&nbsp;", "")

        hyperlink=tableRow[Helpers.GetIndex(columnHeaders, "Hyperlink")]

        # OK, we have all the information we want from this TableRow (a single issue of a fanzine).
        # Add it to the standardized fanzine list.
        if title in standardizedFanzines:
            standardizedFanzines[title].append(IssueData(date, issueTitle, hyperlink, directory))
        else:
            standardizedFanzines[title] = [IssueData(date, issueTitle, hyperlink, directory)]


# Next we walk the list of singe-issue directories and try to extract the needed information
for directory in singleIssueDirectories:
    print(directory + " ...processing")

    # There should be an index.html file.  Open it.
    indexfilename=os.path.join(dirname, directory, "index.html")
    if not os.path.isfile(indexfilename):
        print("******Missing: "+indexfilename)
        continue

    # Read the index.html file.
    with open(indexfilename, "r") as file:
        contents=file.read()

    success=False

    # Case 1:   The issue information is an an <h2> block, which consists of several bits of information separated by one or more <BR>s.
    #           The title is typically first, and there may be a date in there somewhere.
    # The index.html page itself is the URL we need to use
    t=Helpers.ExtractTaggedStuff(contents, 0, "body")
    if t is not None:
        contents=t[0]
        t=Helpers.ExtractTaggedStuff(contents, 0, "h2")
        if t is not None:
            h2=t[0]
            h2s=h2.split("<BR>")
            title=h2s[0]
            # Walk through the chunks of H2 looking for something that parses like a date
            for i in range(1, len(h2s)):
                date=Helpers.InterpretDate(h2s[i])
                if date is not None:
                    if title in standardizedFanzines:
                        standardizedFanzines[title].append(IssueData(date, title, "index.html", directory))
                    else:
                        standardizedFanzines[title] = [IssueData(date, title, "index.html", directory)]
                    success=True
                    break



#=================================
# Step 3

# Now it's time to generate output.
# We must convert the data in standardizedFanzines into something suitable for sorting, which means a list of tuples
# We create a list of tuples (fanzine title, issue date, issue title, issue hyperlink)
sortableListOfIssues=[]
for title in standardizedFanzines:
    issueList=standardizedFanzines[title]
    for issue in issueList:
        sortableListOfIssues.append((title, issue.date, issue.title, issue.hyperlink, issue.directory))

sortableListOfIssues=sorted(sortableListOfIssues, key=lambda tp: tp[1])

# Now print the list
out=open("output data.txt", "w")
for item in sortableListOfIssues:
    print(str(item[1])+"  \t"+str(item[0])+"  \t"+str(item[2])+"  \t"+str(item[4])+"/"+str(item[3]), file=out)
out.close()
i=0
