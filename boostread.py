import os, sys
from shutil import copyfile

# Flag to give a prompt to push to git
PushToGit = True
# User to get the path of the python file itself and not where it is being executed from
curDir = sys.path[0]

# Creates the directory if it doesn't already exist
try:    os.mkdir(curDir + "/markdown")
# If the file exists, nothing needs to be done
except FileExistsError: pass

# Walking over the directory
for root, dirs, files in os.walk(curDir + "/notes"):
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
        folderName = curDir + "/markdown/"

        # Open the file and interate over the lines
        with open(curDir + "/notes/" + filename,"r") as file:
            for line in file:
                line = line.strip()

                # Get the outputname from the title and replace spaces with underscores
                if "title: " in line:
                    outputName = line[8:-1].replace(" ", "_")

                # Read the first tag as the subfolder
                elif "tags" in line and "]" not in line:
                    folderName  += (file.readline().strip()[1:-1] + "/").replace(" ","_")
                    # Create the subfolder if it doesn't exist
                    try: os.mkdir(folderName)
                    # If the file exists, nothing needs to be done
                    except FileExistsError: pass
                
                # If the line starts with 'content: ' then the next block is what we need to write
                elif "content: '''" in line:
                    # Create a file and open it
                    output = open(folderName + outputName + ".md","w")
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
                elif "content: \"" in line:
                    print("[NOTE] Single line files are not supported.")
                
                # the write flag is true, write the line to the output
                if write:
                    # there is an embeded image
                    if ":storage/" in line:
                        
                        # Create a src directory for storing images
                        try: os.mkdir(curDir + "/markdown/src")
                        # If the directory already exists, nothing needs to be done
                        except FileExistsError: pass

                        # Creating values to store the start and the end of the image reference
                        emebededStart = 0
                        embededEnd = len(line)-1
                        # Move up or down the line until reaching the start or end of the reference
                        while line[emebededStart] != "/":  emebededStart+=1
                        while line[embededEnd] != "/":   embededEnd-=1
                        # Get the source and destination directories for the file to be embeded
                        src = curDir + "/attachments/" + line[emebededStart+1:-1]
                        dst = curDir + "/markdown/src" + line[embededEnd:-1]
                        # Copy the file to the markdown/src folder
                        copyfile(src, dst)
                        # Editing the embed reference to be relative to the file 
                        output.write(line[:emebededStart-8] + "../src" + line[embededEnd:] + "  \n")
                    # If there are no files embeded on the line, just write it to the output
                    else:   output.write(line + "  \n")

# If the user wants to push to git
if PushToGit:
    # Check the user actually wants to push to git
    pushQuery = input("Do you want to push to github repo? [y/n]: ")
    if pushQuery.lower() in ["y","yes"]:
        # Get a commit message from the user
        message = input("Enter a commit message: ")
        # cd into the directory, add all the files, commit with the specified message, and push
        os.system("cd {0}/markdown;git add .;git commit -m \"{1}\";git push".format(curDir, message))