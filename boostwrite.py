import os, sys, argparse, json, re, time
from shutil import copyfile
from pathlib import Path
from binascii import hexlify
from datetime import date


def alphanumKey(key):
    return [int(c) if c.isdigit() else c for c in re.split('([0-9]+)', key)]


# Getting the default path
DEFAULT_PATH = str(Path.home()) + "/Documents"
DEFAULT_TAG = "\0"*100


# Creates a parser for system arguments
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--dir", default=None, help="The directory where the program will run from the default path (currently \"{0}\")".format(DEFAULT_PATH))
parser.add_argument("-f", "--fdir", default=None, help="The full directory to where the program will run")
parser.add_argument("-q", "--quiet", action="store_true", help="Will not prompt if no tags are given or files are one line long.")
parser.add_argument("-t", "--tags", action="store_true", help="If the notes are using tags as subfolders")

args = parser.parse_args()


TAGS = args.tags
# The full directory argument takes priority
if args.fdir is not None:
    directory = args.fdir
# Then the "From default directory" tag
elif args.dir is not None:
    directory = DEFAULT_PATH + args.dir
# If no directory tags are given, use the path for the program
else:
    directory = sys.path[0]


# Create a dictionary to find the folder names
folderNameDict = {}
# Open the json file that stores the folder names
config = json.load(open(directory + "/boostnote.json"))
# Create a dictionary for the folder names and their keys
for f in config["folders"]:
    folderNameDict[f["name"]] = f["key"]

# Creates the directory if it doesn't already exist
try:    os.mkdir(directory + "/notes")
# If the file exists, nothing needs to be done
except FileExistsError: pass
# Creates the directory if it doesn't already exist
try:    os.mkdir(directory + "/attachments")
# If the file exists, nothing needs to be done
except FileExistsError: pass

target = "../../src" if TAGS else "../src"



# Walking over the directory
for root, dirs, files in os.walk(directory + "/markdown"):
    # Iterating over all the filenames
    for filename in files:

        if ".md" not in filename:
            continue    

        # print(hexlify(filename.encode()))
        tag = ""
        if TAGS:
            tag = root.split("/")[-1]
            folder = folderNameDict[root.split("/")[-2]]
        else:
            folder = folderNameDict[root.split("/")[-1]]
        

        with open(root + "/" +filename,"r") as file, open(directory + "/notes/" + filename[:-2] + "cson","w") as out:
            t = time.strftime("%Y-%m-%dT%H:%M:%S.{0}Z").format(str(int(round(time.time() * 1000)))[-3:])
            out.write("createdAt: \"{}\"\n".format(t))
            out.write("updatedAt: \"{}\"\n".format(t))
            out.write("type: \"MARKDOWN_NOTE\"\n")
            out.write("folder: \"{}\"\n".format(folder))
            out.write("title: \"{}\"\n".format(filename[:-3].replace("_"," ")))
            out.write("tags: [\n  \"{0}\"\n]\n".format(tag) if TAGS else "tags: []\n")
            out.write("content: '''\n")

            # input(filename)
            for line in file:
                # Fully stripped to get the parameters and end stripped for content
                lineStr = line.replace("  \n", "")
                if target in lineStr:
                    try:    os.mkdir(directory + "/attachments/{0}".format(filename[:-3]))
                    except FileExistsError: pass

                    img = lineStr
                    while img[1] != "(":
                        img = img[1:]
                    src = directory + img[2:-1].replace(target[:-4], "/markdown")
                    dst = directory + "/attachments/{0}/{1}".format(filename[:-3], src.split("/")[-1]) 
                    copyfile(src, dst)
                    lineStr = lineStr.replace(target, ":storage/{0}".format(filename[:-3]))

                out.write("  " + lineStr + "\n")

            out.write("'''\n")
            out.write("linesHighlighted: []\n")
            out.write("isStarred: false\n")
            out.write("isTrashed: false\n")