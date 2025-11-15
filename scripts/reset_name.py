"""
detect incorrectly named audio files and rename them
"""

import os
import sys

# directory_name = None


try:
    directory_name = sys.argv[1]
    print("your directory name is:", directory_name)
    contents = os.listdir(directory_name)
    print("the contents of", directory_name, "are: ", contents)
    renamebool = input("would you like to rename these files? enter Y or N: ").lower()
    if renamebool == "y":
        print("ok lets start")
    elif renamebool == "n":
        print("exiting..")
    else:
        print("invalid reponse")

    new_name = input(f"what would you like to rename {contents[0]}?")
    old_path = os.path.join(directory_name, contents[0])  # better for cross platform
    new_path = os.path.join(directory_name, new_name)
    print(f"renaming {old_path} to {new_path}...")
    try:
        os.rename(f"{directory_name}/{contents[0]}", f"{directory_name}/{new_name}")
        contents = os.listdir(directory_name)
        print("done! the contents of", directory_name, "are: ", contents)
    except:
        print("could not rename")

except:

    print("please pass directory_name")
