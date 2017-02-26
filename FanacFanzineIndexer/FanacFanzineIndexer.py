import tkinter
from tkinter import filedialog
import os
import os.path
import xml.etree.ElementTree as ET

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

# Walk the list of directories
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

    # Try to find the first two tables
    start1=contents.lower().find("<table")
    end1=contents.lower().find("</table>", start1)
    start2=contents.lower().find("<table", end1)
    end2=contents.lower().find("</table>", start2)

    table1=contents[start1:end1+8]
    table2=contents[start2:end2+8]

    # Eliminate <p> and </p>.  The former because they are usually not closed by a </p> and the latter because sometimes they are.
    table1=table1.replace("<p>","").replace("<P>","").replace("</p>","").replace("</P>","")
    table2=table2.replace("<p>","").replace("<P>","").replace("</p>","").replace("</P>","")

    i=0
