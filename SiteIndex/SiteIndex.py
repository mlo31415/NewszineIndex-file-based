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
singleIssueDirectories=["Acolyte"]

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

    # The most common directory index.html format consists of three tables.
    # The top table holds the top navigation buttons.
    # The middle table holds the rows of issue links.
    # The bottom table holds the bottom navigation buttons. (This table can safely be ignored.)
    # Read the index.html file and located the first two tables.
    with open(indexfilename, "r") as file:
        contents=file.read()
    i=0