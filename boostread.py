import os, sys, argparse
from shutil import copyfile
from collections import defaultdict
from pathlib import Path

# Flag to give a prompt to push to git
PUSH_TO_GIT_PROMPT = True
AUTO_GENERATE_README = True
DEFAULT_PATH = str(Path.home()) + "/Documents"

# Creates a parser for system arguments
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--dir", default=None, help="The directory where the program will run from the default path (currently \"{0}\")".format(DEFAULT_PATH))
parser.add_argument("-f", "--fdir", default=None, help="The full directory to where the program will run")
parser.add_argument("-q", "--quiet", action="store_true", help="Will not prompt if no tags are given or files are one line long.")
args = parser.parse_args()

# The full directory argument takes priority
if args.fdir is not None:
    directory = args.fdir
# Then the "From default directory" tag
elif args.dir is not None:
    directory = DEFAULT_PATH + args.dir
# If no directory tags are given, use the path for the program
else:
    directory = sys.path[0]

# Default dict for storing the names of the folders and items
filesInRepo = defaultdict(list)
# Default tag is empty
tag = ""

# Creates the directory if it doesn't already exist
try:    os.mkdir(directory + "/markdown")
# If the file exists, nothing needs to be done
except FileExistsError: pass

# Walking over the directory
for root, dirs, files in os.walk(directory + "/notes"):
    # Iterating over all the filenames
    for filename in files:
        # If the file is not a .cson file, we move on to the next file
        if ".cson" not in filename:
            continue

        # Set the write flag to false until we reach the content
        write = False
        # Strip off the .cson extension for the default filename
        outputName = filename[:-4]
        # Set the default output folder as markdown
        folderName = directory + "/markdown/"

        # Open the file and interate over the lines
        with open(directory + "/notes/" + filename,"r") as file:
            for line in file:
                # Remove weird new line stuff
                line = line.strip()

                # Get the outputname from the title and replace spaces with underscores
                if "title: " in line:
                    outputName = line[8:-1].replace(" ", "_")

                # Read the first tag as the subfolder
                elif "tags" in line and "]" not in line:
                    tag = (file.readline().strip()[1:-1] + "/").replace(" ","_")
                                    
                # If the line starts with 'content: ' then the next block is what we need to write
                elif "content: '''" in line:
                    # If the tag has not been set and the quiet flag has not been set, ask for a flag
                    if tag == "" and not args.quiet:
                        # Ask the user if they want to add a flag
                        tagQuery = input("File: \"{0}\" has no tag.\nDo you want to add a tag? [y/N]: ".format(outputName))
                        if tagQuery.lower() in ["y","yes"]:
                            # Get the tag from the user
                            tag = input("Enter a tag: ") +  "/"    
                    # Appenf the tag to the folder name
                    folderName += tag    

                    # Create the subfolder if it doesn't exist
                    try: os.mkdir(folderName)
                    # If the file exists, nothing needs to be done
                    except FileExistsError: pass  

                    # Create a file and open it
                    output = open(folderName + outputName + ".md","w")

                    # Add the file to the directory listing
                    if folderName != directory + "/markdown/":
                        filesInRepo[folderName[len(directory + "/markdown/"):-1]].append(outputName)
                    else:
                        filesInRepo["Other_Files"].append(outputName)
                    # Set the write flag to be true
                    write = True
                    # Move on to the next line
                    continue

                # The end of the write block with be denoted by three '
                elif line[:3] == "'''":
                    # Close the file if it was opened
                    if write:
                        output.close()
                    # Set the write flag to false
                    write = False
                
                # If there is only one line of content, let the user know it is not supported
                elif "content: \"" in line and not args.quiet:
                    print("[NOTE] Single line files are not supported. File is:", outputName)
                
                # the write flag is true, write the line to the output
                if write:
                    # there is an embeded image
                    if ":storage/" in line:
                        
                        # Create a src directory for storing images
                        try: os.mkdir(directory + "/markdown/src")
                        # If the directory already exists, nothing needs to be done
                        except FileExistsError: pass

                        # Creating values to store the start and the end of the image reference
                        emebededStart = 0
                        embededEnd = len(line)-1
                        # Move up or down the line until reaching the start or end of the reference
                        while line[emebededStart] != "/":  emebededStart+=1
                        while line[embededEnd] != "/":   embededEnd-=1
                        # Get the source and destination directories for the file to be embeded
                        src = directory + "/attachments/" + line[emebededStart+1:-1]
                        dst = directory + "/markdown/src" + line[embededEnd:-1]
                        # Copy the file to the markdown/src folder
                        copyfile(src, dst)
                        # Editing the embed reference to be relative to the file 
                        output.write(line[:emebededStart-8] + "../src" + line[embededEnd:] + "  \n")
                    # If there are no files embeded on the line, just write it to the output
                    else:   output.write(line + "  \n")

# Check to see if the readme flag is true
if AUTO_GENERATE_README:
    # Create the readme file
    with open(directory + "/markdown/README.md","w") as README:
        # Write the title
        README.write("# Folders  \n")
        # Iterate over all the folders and items that will be uploaded
        for folder, items in filesInRepo.items():
            # Write the subheading
            README.write("  \n## {0}  \n".format(folder))
            # Write the filenames as links
            for name in sorted(items):
                README.write("- [{0}](./{1}/{0})  \n".format(name, folder) if folder != "Other_Files" else "- [{0}](./{0})  \n".format(name))

# If the user wants to push to git
if PUSH_TO_GIT_PROMPT:
    # Check the user actually wants to push to git
    pushQuery = input("Do you want to push to github repo? [y/N]: ")
    if pushQuery.lower() in ["y","yes"]:
        # Get a commit message from the user
        message = input("Enter a commit message: ")
        # cd into the directory, add all the files, commit with the specified message, and push
        os.system("cd {0}/markdown;git add .;git commit -m \"{1}\";git push".format(directory, message))