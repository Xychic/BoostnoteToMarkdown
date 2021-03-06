import os, sys, argparse, json, re, subprocess
from shutil import copyfile
from collections import defaultdict
from pathlib import Path

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
parser.add_argument("-r", "--readme", action="store_true", help="Will autogenerate a README file if flag is set.")
parser.add_argument("-p", "--push-to-git", action="store_true", help="Will automatically push to a GitHub repo.")
parser.add_argument("-R", "--raw", action="store_true", help="Will bundle in the raw .cson files, and if pushing to GitHub, will place them in a backup branch")

args = parser.parse_args()

AUTO_GENERATE_README = args.readme
PUSH_TO_GIT_PROMPT = args.push_to_git
BUNDLE_RAW = args.raw

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
    folderNameDict[f["key"]] = f["name"]

# Default dict for storing the names of the folders and items
filesInRepo = defaultdict(lambda: defaultdict(list))

# Creates the directory if it doesn't already exist
try:    os.mkdir(directory + "/markdown")
# If the file exists, nothing needs to be done
except FileExistsError: pass

if BUNDLE_RAW:
    # Creates the directory if it doesn't already exist
    try:    os.mkdir(directory + "/markdown/raw")
    # If the file exists, nothing needs to be done
    except FileExistsError: pass
    subprocess.run(["ln", "-f", directory + "/boostnote.json", directory + "/markdown/raw/boostnote.json"])
    # print(directory + "/boostnote.json", directory + "/markdown/raw/boostnote.json")

# Walking over the directory
for root, dirs, files in os.walk(directory + "/notes"):
    # Iterating over all the filenames
    for filename in files:
        # Default tag is empty
        tag = ""
        # If the file is not a .cson file, we move on to the next file
        if ".cson" not in filename:
            continue    

        if BUNDLE_RAW:
            # Creates a symbolic link to the raw .cson files in the markdown directory
            subprocess.run(["ln", "-f", 
                root + "/" + filename, 
                directory + "/markdown/raw/" + filename
            ])

        # Set the write flag to false until we reach the content
        write = False
        # Strip off the .cson extension for the default filename
        outputName = filename[:-4]
        # Set the default output folder as markdown
        folderName = directory + "/markdown/"

        # Open the file and interate over the lines
        with open(directory + "/notes/" + filename,"r") as file:
            for line in file:
                # Fully stripped to get the parameters and end stripped for content
                lineStr = line.strip()
                line = line.strip("\n")[2:]


                # Get the folder in which to store the note
                if "folder: " in lineStr:
                    # Store the subfolder name
                    subFolder = folderNameDict[lineStr[9:-1]] + "/"
                    # Add the foldername to the path
                    folderName += subFolder
                    # Create the folder if it doesn't exist
                    try:    os.mkdir(folderName)
                    # If it does exist, do nothing
                    except FileExistsError: pass

                # Get the outputname from the title and replace spaces with underscores
                if "title: " in lineStr:
                    outputName = lineStr[8:-1].replace(" ", "_")

                # Read the first tag as the subfolder
                elif "tags" in lineStr and "]" not in lineStr:
                    tag = (file.readline().strip()[1:-1] + "/").replace(" ","_")

                # If the line starts with 'content: ' then the next block is what we need to write
                elif "content: '''" in lineStr:
                    # If the tag has not been set and the quiet flag has not been set, ask for a flag
                    if tag == "" and not args.quiet:
                        # Ask the user if they want to add a flag
                        tagQuery = input("File: \"{0}\" has no tag.\nDo you want to add a tag? [y/N]: ".format(outputName))
                        if tagQuery.lower() in ["y","yes"]:
                            # Get the tag from the user
                            tag = input("Enter a tag: ") + "/"
                    # Append the tag to the folder name
                    folderName += tag

                    # Create the subfolder if it doesn't exist
                    try: os.mkdir(folderName)
                    # If the file exists, nothing needs to be done
                    except FileExistsError: pass

                    # Create a file and open it
                    output = open(folderName + outputName + ".md","w")

                    # Add the file to the directory listing
                    if tag != "":

                        # If the tag is set
                        filesInRepo[subFolder[:-1]][tag[:-1]].append(outputName)
                    else:
                        filesInRepo[subFolder[:-1]][DEFAULT_TAG].append(outputName)
                    # Set the write flag to be true
                    write = True
                    # Move on to the next line
                    continue

                # The end of the write block with be denoted by three '
                elif lineStr[:3] == "'''":
                    # Close the file if it was opened
                    if write:
                        output.close()
                    # Set the write flag to false
                    write = False

                # If there is only one line of content, let the user know it is not supported
                elif "content: \"" in lineStr and not args.quiet:
                    print("[NOTE] Single line files are not supported. File is:", outputName)

                # the write flag is true, write the line to the output
                if write:
                    # there is an embeded image
                    if ":storage/" in lineStr:

                        # Create a src directory for storing images
                        try: os.mkdir(directory + "/markdown/src")
                        # If the directory already exists, nothing needs to be done
                        except FileExistsError: pass

                        # Creating values to store the start and the end of the image reference
                        emebededStart = 0
                        embededEnd = len(lineStr)-1
                        # Move up or down the line until reaching the start or end of the reference
                        while lineStr[emebededStart] != "/":  emebededStart+=1
                        while lineStr[embededEnd] != "/":   embededEnd-=1
                        # Get the source and destination directories for the file to be embeded
                        src = directory + "/attachments/" + lineStr[emebededStart+1:-1]
                        dst = directory + "/markdown/src" + lineStr[embededEnd:-1]
                        # Copy the file to the markdown/src folder
                        copyfile(src, dst)
                        # Editing the embed reference to be relative to the file 
                        output.write(lineStr[:emebededStart-8] + ("../../src" if tag != "" else "../src") + lineStr[embededEnd:] + "  \n")
                    # If there are no files embeded on the line, just write it to the output
                    else:   output.write(line + "  \n")


# Check to see if the readme flag is true
if AUTO_GENERATE_README:
    # Create the readme file
    with open(directory + "/markdown/README.md","w") as README:
        # Write the title
        README.write("# Folders  \n")
        # Iterate over all the folders and items that will be uploaded
        for folder, subfolder in sorted(filesInRepo.items(), key=lambda x: alphanumKey(x[0])):
            README.write("  \n## {0}  \n".format(folder))
            for tag, items in sorted(subfolder.items(), key=lambda x: alphanumKey(x[0])):
                if tag != DEFAULT_TAG:  
                    README.write("  \n### {0}  \n".format(tag))
                else:
                    README.write("  \n###  \n")
                for name in sorted(items, key=alphanumKey):
                    README.write("- [{0}](./{1}/{2}/{0}.md)  \n".format(name, folder, tag) if tag != DEFAULT_TAG else "- [{0}](./{1}/{0}.md)  \n".format(name, folder))

# If the user wants to push to git
if PUSH_TO_GIT_PROMPT:
    # If no git repository exists
    if not os.path.exists(directory + "/markdown/.git"):
        # Ask the user if they want to intialise a git repo
        createRepoQuery = input(directory + "/markdown Is not a GitHub repo, do you want to initalise one? [y/N]: ")
        if createRepoQuery.lower() in ["y", "yes"]:
            # Get required information to link to GitHub
            username = input("Enter your GitHub username: ")
            reponame = input("Enter the name of the repo to link to: ")
            message = input("Enter a commit message: ")

            # cd into directory, initialise git repo, connect to remote, add files to master branch, and push
            os.system("cd {0}/markdown; git init; git remote add origin git@github.com:{1}/{2}.git; git add *[^raw]; git commit -m \"{3}\"; git push -u origin master".format(
                directory, username, reponame, message))
            if BUNDLE_RAW:  os.system("cd {0}/markdown; git checkout -b backup; git add .; git commit -m \"{1}\"; git push -u origin backup".format(directory, message))

        # git init
        # git remote add origin git@github.com:[USERNAME]/[REPONAME].git
        # git add .
        # git commit -m [MESSAGE]
        # git push --set-upstream origin master
    else:
        # Check the user actually wants to push to git
        pushQuery = input("Do you want to push to GitHub? [y/N]: ")
        if pushQuery.lower() in ["y","yes"]:
            # Get a commit message from the user
            message = input("Enter a commit message: ")
            # cd into the directory, add all the files, commit with the specified message, and push
            os.system("cd {0}/markdown; git checkout master; git add *[^raw]; git commit -m \"{1}\"; git push -u origin master".format(directory, message))
            
            # If the raw .cson files are being bundled
            if BUNDLE_RAW:  
                # Check to see if the backup branch has been created
                if "backup" not in subprocess.check_output(["git", "branch"], cwd="{0}/markdown".format(directory), text=True):    
                    # Create the branch if necessary
                    subprocess.run(["git", "branch", "backup"], cwd="{0}/markdown".format(directory))
                # Add all the files to the backup branch
                os.system("cd {0}/markdown; git checkout backup; git add .; git commit -m \"{1}\"; git push -u origin backup".format(directory, message))