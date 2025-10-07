import random
import string
import zipfile
import os
from website_youtube_dl.common.youtubeAPI import (FormatMP3,
                                                  Format360p,
                                                  Format480p,
                                                  Format720p,
                                                  Format1080p,
                                                  Format2160p)
from flask import current_app as app

def get_format_instance(format_str):
    format_classes = {
        "mp3": FormatMP3,
        "360p": Format360p,
        "480p": Format480p,
        "720p": Format720p,
        "1080p": Format1080p,
        "2160p": Format2160p,
    }
    if format_str not in format_classes:
        app.logger.error(f"{format_str} not supported")
        format_str = "mp3"
    return format_classes.get(format_str)()


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


