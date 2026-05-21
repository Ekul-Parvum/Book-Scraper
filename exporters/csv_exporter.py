# This file contains some utility functions for exporting book data into a csv

import config.config as config
import os

configJson = config.getConfigsFromJson()

# generateCsvFilePath - generates a path to the csv file we are saving to. Generates a new file there if there is not allready one.
# Parameters:
#       outputFolderPath - path to the folder the .csv will be in.
# returns: the file path as a string
# Error Handling: None
def generateCsvFilePath(outputFolderPath):
    return os.path.join(outputFolderPath, configJson["outputFileName"] + "CSV.csv")

# savePageToCSV - saves the given page to the csvFile.
# Parameters:
#       bookObjs - array of books on the current page.
#       csvWriter - used to write to csvFile
# Returns: Void
# Error Handling: None
def savePageToCSV(bookObjs, csvWriter):
    for book in bookObjs:
        csvWriter.writerow(book.getRowOfData())