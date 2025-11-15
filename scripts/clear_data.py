import os
import shutil


def clear_dir(folder):
    folder = folder
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print("Failed to delete %s. reason: %s" % (file_path, e))


def clear_json():
    file = "audiolist.json"

    file_path = os.path.join(os.getcwd(), file)

    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"File {file} deleted.")
        except Exception as e:
            print("Failed to delete %s. reason: %s" % (file_path, e))
    else:
        print(f"File '{file}' not found in the current directory.")
