import zipfile
import os


def get_files_from_dir(dirPath):
    return [f.split(".")[0] for f in os.listdir(dirPath)
            if os.path.isfile(os.path.join(dirPath, f))]


def zip_all_files_in_list(direcoryPath, playlist_name, listOfFilePaths):  # pragma: no_cover
    type_of_compres = "zip"
    zip_file_full_path = os.path.join(direcoryPath,
                                      playlist_name)
    with zipfile.ZipFile(f"{zip_file_full_path}.{type_of_compres}", "w") as zipInstance:
        for filePath in listOfFilePaths:
            zipInstance.write(filePath, filePath.split("/")[-1])
    return f"{zip_file_full_path.split('/')[-1]}.{type_of_compres}"
