# Boostnote to Markdown  
  
## What the script does  
This program can convert a all your boostnote notes to raw markdown (.md) files. It will copy any images into a `src` folder and change all the references to be relative, which means there is one folder for all your notes and media embedded in said notes.  
  
## What the script doesn't do  
Unfortunately it cannot make your notes look good. It simply copies whatever formatting you have applied yourself.  
  
## Usage  
Simply run this program in the directory containing the "notes" folder containing the ".cson" files boostnote has created. It will create a new directory called "markdown" which will store all the notes it has converted. The first tag any note has will be used as the name of the subfolder to store the note. If no tags are set, the user will be asked if they want to give a tag, if they don't then it will not be stored in any subfolders and simply placed in the default directory.  

# Possible flags  
`-d` `--dir`    Used to specify the path to the directory where the notes folder is, from the users documents folder  
`-f` `--fdir`   Used to specify the full path to the directory where the notes folder is, overwrites whatever is set by -d/--dir  
`-q` `--quiet`  Used to supress warnings about single line files and notes without flags  
`-r` `--readme`     If set will auto-generate a README file with relative links to each file  
`-p` `--push-to-git`    If set will push to a linked GitHub repo or show a prompt to link to an existing repository  
`-R` `--raw`  Will bundle in the raw `.cson` files, and if pushing to GitHub, will place them in a `backup` branch
  
## Setting up GitHub integration  
Simply create the repository on GitHub and run the program with the push to GitHub flag as True. If the directory is not set up for GitHub, it will give you a prompt asking you to enter your username, the name of the repository you want to link it to and a commit message.  
