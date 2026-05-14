import csv
import config.config as config
import os

def generateCsvFilePath(outputFolderPath):
    return os.path.join(outputFolderPath, config.outputFileName + "CSV.csv")

def savePageToCSV(bookObjs, csvWriter):
    for book in bookObjs:
        csvWriter.writerow(book.getRowOfData())