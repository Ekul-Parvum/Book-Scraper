# This file contains utility functions for exporting book data into a .json

import config.config as config
import os
import json

configJson = config.getConfigsFromJson()

def generateJsonFilePath(outputFolderPath):
    return os.path.join(outputFolderPath, configJson["outputFileName"] + "JSON.json")

def savePageToJSON(bookObj, jsonFile):

    # Array of dictionaries we are puting in the json file:
    data = []

    # Put a dictionary from each book into the data array:
    for book in bookObj:
        data.append(book.getDictionaryOfBook())

    # And then save data to the jsonFile:
    json.dump(data, jsonFile, indent=4, ensure_ascii=False)