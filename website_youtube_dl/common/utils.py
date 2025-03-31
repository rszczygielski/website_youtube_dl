import zipfile
import os


def getFilesFromDir(dirPath):
    return [f.split(".")[0] for f in os.listdir(dirPath) if os.path.isfile(os.path.join(dirPath, f))]


def zipAllFilesInList(direcoryPath, playlistName, listOfFilePaths):  # pragma: no_cover
    typeOfCompres = "zip"
    zipFileFullPath = os.path.join(direcoryPath,
                                   playlistName)
    with zipfile.ZipFile(f"{zipFileFullPath}.{typeOfCompres}", "w") as zipInstance:
        for filePath in listOfFilePaths:
            zipInstance.write(filePath, filePath.split("/")[-1])
    return f"{zipFileFullPath.split('/')[-1]}.{typeOfCompres}"