import os, sys
from shutil import copyfile

PushToGit = True
curDir = sys.path[0]

try:
    os.mkdir(curDir + "/markdown")
except:
    pass

for root, dirs, files in os.walk(curDir + "/notes"):
    for filename in files:
        if ".cson" not in filename:
            continue

        textToWrite = ""
        write = False
        level = 0
        outputName = filename[:-4]
        folderName = curDir + "/markdown/"
        with open(curDir + "/notes/" + filename,"r") as file:
            for line in file:
                if "title: " in line:
                    outputName = line[8:-2].replace(" ", "_")
                elif "tags" in line and "]" not in line:
                    folderName  += (file.readline().strip()[1:-1] + "/").replace(" ","_")
                    try:
                        os.mkdir(folderName)
                    except:
                        pass
                elif "content: '''" in line:
                    output = open(folderName + outputName + ".md","w")
                    write = True
                    continue
                elif line[:3] == "'''":
                    if write:
                        output.close()
                    write = False
                elif "content: \"" in line:
                    print("[NOTE] Single line files are not supported.")
                if write:
                    if ":storage/" in line:
                        try:
                            os.mkdir(curDir + "/markdown/src")
                        except:
                            pass
                        i = 0
                        j = len(line)-1
                        while line[i] != "/":  i+=1
                        while line[j] != "/":   j-=1
                        src = curDir + "/attachments/" + line[i+1:-2]
                        dst = curDir + "/markdown/src" + line[j:-2]
                        copyfile(src, dst)
                        output.write(line[2:i-8] + "../src" + line[j:-2] + ")\n")
                    else:
                        output.write(line[2:])


if PushToGit:
    pushQuery = input("Do you want to push to github repo? [y/n]")
    if pushQuery.lower() in ["y","yes"]:
        message = input("Enter a commit message: ")
        os.system("cd {0}/markdown;git add .;git commit -m \"{1}\";git push".format(curDir, message))