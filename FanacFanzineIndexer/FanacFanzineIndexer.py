import tkinter
from tkinter import filedialog
import os
import os.path
import xml.etree.ElementTree as ET
import Helpers

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
singleIssueDirectories=["Abstract", "Acolyte"]

# Get a list of all the directories in the directory.
dirList = [f for f in os.listdir(dirname) if os.path.isdir(os.path.join(dirname, f))]

# Walk the list of directories and create fanzines
# fanzines is a dictionary (indexed by name) with each element being a list of row tuples
fanzines={}

for dir in dirList:
    print(dir+" ...processing")
    if dir in singleIssueDirectories:
        print("   This is a single issue directory. Skipping.")
        continue

    # There should be an index.html file.  Open it.
    indexfilename=os.path.join(dirname, dir,"index.html")
    if not os.path.isfile(indexfilename):
        print("  ***Missing: "+indexfilename)
        continue

    # The most common directory index.html format
    # <title></title> tagging the fanzine's display name
    # Some page info in <h2></h2>
    #   (Sometimes some untagged bumpf following this.)
    # A top table which holds the top navigation buttons and can be ignored.
    # A middle table which holds the rows of issue links.
    # A bottom table holds the bottom navigation buttons and can be ignored, also.
    # Some more untagged bumpf included who scanned it and the update date.

    # Read the index.html file.
    with open(indexfilename, "r") as file:
        contents=file.read()

    # Get the <title>
    t=Helpers.extractTaggedStuff(contents, 0, "title")
    if t == None:
        print("  ***Could not find <title>...</title>.  Aborting.")
        continue
    title=t[0]
    loc=t[1]

    # Try to find the first two tables
    t=Helpers.extractTaggedStuff(contents, loc, "table")    # Ignored first table
    if t == None:
        print("  ***Could not find first <table>.  Aborting.")
        continue
    loc=t[1]
    t=Helpers.extractTaggedStuff(contents, loc, "table")
    if t == None:
        print("  ***Could not find second <table>.  Aborting.")
        continue
    tableText=t[0]
    loc=t[1]

    # Eliminate <p> and </p>.  The former because they are usually not closed by a </p> and the latter because sometimes they are.
    tableText=tableText.replace("<p>", "").replace("<P>", "").replace("</p>", "").replace("</P>", "")
    # Eliminate /n
    tableText=tableText.replace("\n", "")

    # OK, start decoding the index table.

    # The first row (bounded by <tr> tags) should be column headers bounded by <th> tags.
    # We will loop until we run out of <th> tags
    columns=[]
    t=Helpers.extractTaggedStuff(tableText, 0, "tr")
    if t == None:
        print("  ***Could not find coumn headers row.  Aborting.")
        continue
    headers=t[0]
    endheaders=t[1]
    loc=0
    while True:
        t=Helpers.extractTaggedStuff(headers, loc, "th")
        if t == None:
            break
        columns.append(t[0])
        loc=t[1]

    print("   "+str(columns))

    table=[]
    table.append(columns)
    # OK. Now we decode the rows.  There should be one cell for each header column in each row.  The rows will be saved as a list of tuples.
    loc=endheaders
    while True:     # Loop over rows
        row=()
        t=Helpers.extractTaggedStuff(tableText, loc, "tr")
        if t == None:
            break
        rowText=t[0]
        endrow=t[1]
        if t == None:
            break
        loc=0
        while True: # Loop over columns in row
            t = Helpers.extractTaggedStuff(rowText, loc, "td")
            if t == None:
                break
            row=row+(t[0],)
            loc = t[1]
        loc=endrow
        table.append(row)

    fanzines[title]=table

# OK, now we've inhaled the structure of the fanzines part of the website.  Time to make sense of it
# Unfortunately, the website is pretty sloppy and uses different headings on different pages for the same data, so we need to deal with that
# Here is the tables of synomyms
synonyms={
    "Month" : "Month",
    "Mo." : "Month",
    "Quarter/Month" : "Month",
    "Season" : "Month",
    "Issue" : "Issue",
    "#" : "Issue",
    "Num" : "Issue",
    "Number": "Issue",
    "No" : "Issue",
    "Year" : "Year",
    "Volume" : "Volume",
    "Vol" : "Volume",
    "Vol." : "Volume",
    "Vol/#" : "Volume",
    "Vol./#" : "Volume",
    "Day" : "Day",
    "Date" : "Date",
    "Issue Date" : "Date"
}

# We want to make sure we catch all the useful data, so we also have a list of columns we will ignore.
ignoreColumns=["Headline", "Pages", "Notes", "Title", "Type", "PDF Size", "Description", "Country", "Editor/Publisher", "Contains", "Editor", "Editors",
               "Editor/s", "Author/Artist", "Repro", "Publication", "Pp.", "PoB", "LGP", "GP", "Size", "Publisher", "Fanzine", "APA", "Page", "Zine",
               "Author", "Art by", "Story by", "Type of Material", "Reprinted from:", "Content", "Sub-Title"]

# For each issue, we want the following:
#   Date
#   Issue designator (Vol/Num or just Num)
#   HTML link

# The data will be stored in a new dictionary with the same structure as "fanzines"
standardized={}

# Walk the fanzines dictionary and extract the data to create the standardized version
for title in fanzines:
    table=fanzines[title]
    firstTime=True
    columnHeaders=[]
    for tableRow in table:
        if firstTime:
            # The first item in the table is the column headers, but we need to convert these to their standard forms
            for header in tableRow:
                if header in ignoreColumns:
                    columnHeaders.append("ignored")
                else:
                    if header in synonyms:
                        columnHeaders.append(synonyms[header])
                    else:
                        print("   ***Column header not recognized:  "+header)
            firstTime=False


# The next step is to try to make sense of the date information and to generate a date for each issue.


i=0
