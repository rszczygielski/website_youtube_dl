import zipfile
import os
import random
import string


def get_files_from_dir(dirPath):  # pragma: no_cover
    return [f.split(".")[0] for f in os.listdir(dirPath)
            if os.path.isfile(os.path.join(dirPath, f))]


def zip_all_files_in_list(direcoryPath, playlist_name, listOfFilePaths):  # pragma: no_cover
    type_of_compres = "zip"
    zip_file_full_path = os.path.join(direcoryPath, playlist_name)
    with zipfile.ZipFile(f"{zip_file_full_path}.{type_of_compres}", "w") as zipInstance:
        for filePath in listOfFilePaths:
            zipInstance.write(filePath, filePath.split("/")[-1])
    return f"{zip_file_full_path.split('/')[-1]}.{type_of_compres}"


def generate_title_template_for_youtube_downloader(downloaded_files, title):
    counter = 1
    orig_title = title
    while title in downloaded_files:
        counter += 1
        title = f"{orig_title} ({counter})"
    if counter > 1:
        return f"/%(title)s ({counter})"
    return "/%(title)s"

def generate_hash():
    return ''.join(random.sample(string.ascii_letters + string.digits, 6))