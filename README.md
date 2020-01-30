# BoostnoteToMarkdown
Simple python program for extracting the markdown file from boostnotes .cson files

Just save and run this program in the same directory as boostnotes "notes" folder.

Will create a folder called markdown and will use the first tag as the subfolder

Has the option to automatically commit to github if ssh keys are set up and the markdown folder is set up as a git repo

If you choose to automatically commit to github and the AUTO_GENERATE_README flag is true will create a readme to navigate to the files
