# This file containts all the functions used to save the book data to a workbook, and then save that data.

import os                       # For handling filesystem stuff
import logging                  # For loging errors.
import config.config as config                   # Config File - has all my constants/settings

configJson = config.getConfigsFromJson()

# makeWorkBookSheet - Compiles all the given book objects into an excel sheet
# Parameters:
#       bookObjs - Array of all the book objects to put into the exvel sheet
#       pageNum - The page number the books are from, and the page this excel sheet will be
#       sheet - The sheet object that the bookObjs will be put into.
# Returns: Nothing
# Error Handling: None
def makeWorkBookSheet(bookObjs, pageNum, sheet):
    # Making the sheet:
    sheet.title = str(pageNum) + " pages of books"

    sheet.append(["", ""])
    sheet.append(["Page: " + str(pageNum), ""])
    sheet.append(["", ""])

    # Making a header:
    sheet.append(["Title", "Price"])

    # Looping through each book:
    for book in bookObjs:
        sheet.append(book.getRowOfData())

# savePageToWorkbook - Saves the given page to the given workbook
# Parameters:
#       workbook - The workbook which the page will be saved to
#       page - the page to be saved
#       pageNumber - The page number that we are on
# Returns: Nothing directly, just modifies the workbook
# Error Handling: None
def savePageToWorkbook(workbook, page, pageNumber):
    # Setting sheet to the currenlty active sheet:
    sheet = workbook.active

    makeWorkBookSheet(page, pageNumber, sheet)

# savingToExcelDoc - Saves the current workBook to an excel
# Parameters:
#       workBook - the workBook to be saved
# Returns: void
# Error Handling: Logs errors internaly, raises generic exception.
def savingToExcelDoc(workBook, outputFolderPath):

    #excelDocName = folderPath + outputFileName + ".xlsx"
    excelDocName = os.path.join(outputFolderPath, configJson["outputFileName"] + "EXCEL.xlsx")

    print("Saving to: " + excelDocName)

    try:
        workBook.save(excelDocName)
    except Exception as e:
        logging.error(f"Faled to save workbook. {e}")
        raise Exception("Failed to save to Excel")
    
    # Log where the workbook is saved to:
    logging.info(f"Workbook saved to {excelDocName}")
    return

