# BoostnoteToMarkdown
Simple python program for extracting the markdown file from boostnotes .cson files

Just save and run this program in the same directory as boostnotes "notes" folder.

Will create a folder called markdown and will use the first tag as the subfolder

Has the option to automatically commit to github if ssh keys are set up and the markdown folder is set up as a git repo

If you choose to automatically commit to github and the AUTO_GENERATE_README flag is true will create a readme to navigate to the files

## Flags
usage: boostread.py [-h] [-d DIR] [-f FDIR] [-q]

optional arguments:
  -h, --help            show this help message and exit
  -d DIR, --dir DIR     The directory where the program will run from the default path (currently "/home/$USER/Documents")
  -f FDIR, --fdir FDIR  The full directory to where the program will run
  -q, --quiet           Will not prompt if no tags are given or files are one line long. 
