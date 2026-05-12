# Auther: Luke Smith
# Description: It scrapes data from https://books.toscrape.com and saves it into several file formats(only excel right now).

""" 
Improvements:

    7. CSV and JSON exports as well

    Lastly. Once the scraper technicaly works, figure out all the "good product" stuff.
            - How would a customer run it? 
            - And what output would they actualy see?
"""

# - - - - - -[ Liberaries: ]- - - - - -
import requests                 # For getting html data from sites

# For saving/formating data into Excel, JSON, and CSV:
from openpyxl import Workbook   # For working with excel

from urllib.parse import urljoin# Has some functions to make working with urls easy
import os                       # For handling filesystem stuff

import time                     # For deleys
import random                   # For random number generator

import logging                  # For loging errors.
# - - - - - - - - - - - - - - - - - - -

# -/- -/- -/-[ Files I made: ]-\- -\- -\-
import scraper.networking as networking
import config.config as config                   # Config File - has all my constants/settings
# -\- -\- -\- -\- -\- -/- -/- -/- -/- -/-

# configLogs - sets up the configs for logging stuff
# Parameters: None
# Returns: void
def configLogs():
    logging.basicConfig(
        filename="logs/scraper.log",
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )
    logging.info("Program has started and logging is configured")

# region Excel Functions

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
    sheet = workbook.active

    makeWorkBookSheet(page, pageNumber, sheet)

# savingToExcelDoc - Saves the current workBook to an excel
# Parameters:
#       workBook - the workBook to be saved
# Returns: void
# Error Handling: Logs errors internaly, raises generic exception.
def savingToExcelDoc(workBook):
    # Save to an excel document
    folderPath = "~/WindowsSucks"   # Linux/WSL file path
    folderPath = os.path.expanduser(folderPath)

    # Create folder if it doesn't exist
    try:
        os.makedirs(folderPath, exist_ok=True)
    except Exception as e:
        logging.error(f"Failed to make directory to save workbook. {e}")
        raise Exception("Failed to save to Excel")

    #excelDocName = folderPath + outputFileName + ".xlsx"
    excelDocName = os.path.join(folderPath, config.outputFileName + ".xlsx")

    print("Saving to: " + excelDocName)

    try:
        workBook.save(excelDocName)
    except Exception as e:
        logging.error(f"Faled to save workbook. {e}")
        raise Exception("Failed to save to Excel")
    
    # Log where the workbook is saved to:
    logging.info(f"Workbook saved to {excelDocName}")
    return

# endregion

# getUserInput - Gets the user input for how many pages the program will look through
# Parameters:
#       pageUrl - Used to figure out the total number of pages on the site
# Returns: The number of pages the user wants to scrape from. -1 If the user wants to quit 
# Error Handling: Doesn't Log. Raises informative exceptions
def getUserInput(pageUrl, session):
    soup = None
    # Get the soup of the page:
    try:
        soup = networking.getSoupRetry(pageUrl, session, config.numOfRetries)
    except Exception as e:
        raise Exception(f"Failed to get soup for userInput. {e}")

    numOfPages = networking.getNumberOfPages(soup)

    if (numOfPages == None):
        raise Exception("Failed to get Pages: Returned None.")
    elif (numOfPages < 0):
        raise Exception("Failed to get Pages: Out of range.")

    print("Total Number of pages: " + str(numOfPages))

    userInput = -1
    while (userInput < 0 or userInput > numOfPages):
        userInput = input("How many pages do you want to scrape?\n(Input 0 to exit the program): ")
        try:
            userInput = int(userInput)
            if (userInput < 0 or userInput > numOfPages):
                print("That number is out of range. Please try again.\n")
                logging.info(f"User input value out of range: {userInput}")
        except:
            print("That is not a valid number. Please try again.\n")
            logging.info("User input was not a number")
            userInput = -1 # Setting it to -1 so the while loop starts over properly

    return userInput

# scrapePages - scrapes all the books from all the pages it needs to
# Parameters:
#       numOfPages - the number of pages it will scrape from
#       session - the session it will use to pull data from the site
#       pageUrl - the url of the current page. Will be incremented to go to next pages
#       pageNum - keeping track of what page number we are on
#       workBook - for saving book data to excel
# Returns - Nothing, just saves stuff to the workBook
# Error Handling: Logs errors and warnings internaly, raises generic exception.
def scrapePages(numOfPages, session, pageUrl, pageNum, workBook):
    # Clear the terminal:
    os.system("clear")

    # Logging start of scraping procedure:
    logging.info(f"Starting to scrape {numOfPages} pages from {pageUrl}.")

    # Progress bar:
    print("Scraping from pages...")
    print("|" + "-"*config.lengthOfBar + "|  (0 / " + str(numOfPages) + ")", end="\r")

    # Loop through each page:
    for index in range(0, numOfPages):

        # Get the soup of the page:
        try:
            soup = networking.getSoupRetry(pageUrl, session, config.numOfRetries)
        except Exception as e:
            # Log warning:
            logging.error(f"Failed to get soup at page {pageNum}. {e}")
            print(f"\nCan not load page {pageNum}.\nCan not go further than page {pageNum - 1}.\nQuiting Program.")
            return

        # Get the books from the current page
        thisPage = networking.getBooksFromPage(soup)

        # If we got stuff from this page:
        if (thisPage != None):
            # Then push the books from this page into the workbook:
            savePageToWorkbook(workBook, thisPage, pageNum)

            # Increment the page:
            for attempt in range(config.numOfRetries):
                try:
                    pageUrl = networking.incrementPageUrl(pageUrl, soup)
                    break
                except Exception as e:
                    logging.warning(f"Failed to increment page. {e}")

                    # Try reloading the page before attempting to increment again:
                    try:
                        soup = networking.getSoupRetry(pageUrl, session, config.numOfRetries)
                    except Exception as e:
                        logging.error(f"Failed to get soup. {e}")
                        print(f"\nCan not reload page {pageNum}.\nCan not go further than page {pageNum - 1}.\nQuiting Program.")
                        return
            else:
                # If we go through all our attempts, and still cant increment the page, just give up
                logging.error(f"All attempts to increment page {pageNum} have failed. Returning to main")
                # Need to let user know we can't go any further:
                print(f"\nCan not find URL to page {pageNum}.\nCan not go further than page {pageNum - 1}.\nQuiting Program.")
                return
                
            # Keep track of what page number we are on:
            pageNum += 1

            # And we update the loading bar:
            numOfEquals = int((config.lengthOfBar/numOfPages) * (index + 1))
            numOfDashes = config.lengthOfBar - numOfEquals
            print("|" + "="*numOfEquals + "-"*numOfDashes + "|  (" + str(index + 1) + " / " + str(numOfPages) + ")", end="\r")
        else:
            # Log error for when getBooksFromPage() returns none:
            logging.warning("Failed to get books from page " + str(index + 1) + ".")
        
        # Rate Limit:
        time.sleep(random.uniform(0.5, 1.5))

    # Move down a line so that we don't print over the loading bar:
    print("\n")

    # Log successfull completion of scrape:
    logging.info("Scrape completed smoothly")

    return


# main - One function to rule them all
# Parameters: None
# Returns: void
# Error Handling: Logs Info. Raises informative exceptions
def main():
    # Clearing the terminal:
    os.system("clear")

    # Start a session:
    session = requests.Session()

    # Make session look more human:
    session.headers.update({
        "User-Agent": "Mozilla/5.0"
    })

    # - - - [ Variables:  ] - - - 
    pageUrl = "https://books.toscrape.com"      # The URL of the page we are currently on
    numOfPages = None
    workBook = Workbook()                       # Workbook for saving the data into an excel doc
    pageNum = 1                                 # The page number of the page we are currently on
    # - - - - - - - - - - - - - - 
    
    # Getting the user input:
    try:
        numOfPages = getUserInput(pageUrl, session) # Gets user input for the number of pages to scrape data from
    except Exception as e:
        # raising Exception:
        raise Exception(f"Failed to get user input. Quiting main. {e}")

    # If the number of pages is 0, then the user wants to exit the program:
    if (numOfPages == 0):
        logging.info("User is quiting the program")
        return

    # Try to scrape pages:
    try:
        scrapePages(numOfPages, session, pageUrl, pageNum, workBook)
    except Exception as e:
        # Raising exception:
        raise Exception(f"Failed to scape books: {e}")
    

    try:
        savingToExcelDoc(workBook)
    except:
        print("Failed to save to Excel")

    return

# Setting up logs:
configLogs()

# Calling the main function to start the program:
try:
    main()
    print("Thank you for using this program!")
except Exception as e:
    logging.error(f"Main() ran into an error: {e}")
    print("Program has failed to run. \nPlease check that there are no network issues and that the site has not changed since this program was writen.")

# Logging end of program:
logging.info("End of program.")