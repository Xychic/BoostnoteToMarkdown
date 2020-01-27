import os

try:
    os.mkdir("./markdown")
except:
    pass

for root, dirs, files in os.walk("./notes"):
    for filename in files:
        if ".cson" not in filename:
            continue

        textToWrite = ""
        write = False
        level = 0
        outputName = filename[:-4]
        folderName = "./markdown/"
        with open("./notes/" + filename,"r") as file:
            for line in file:
                if "title: " in line:
                    outputName = line[8:-2].replace(" ","_")
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
                if write:
                    output.write(line[2:])
