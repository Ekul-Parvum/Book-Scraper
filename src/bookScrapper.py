# Auther: Luke Smith
# Description: It scrapes data from https://books.toscrape.com and saves it into several file formats(only excel right now).

""" 
Improvements:
    6. Put everything together into a simulated final product, with an executable and everything.
    
"""

# - - - - - -[ Liberaries: ]- - - - - -
import requests                 # For getting html data from sites

from openpyxl import Workbook   # For working with excel
import csv                      # For working with CSV
import json                     # For working with JSON

import os                       # For handling filesystem stuff

import time                     # For deleys
import random                   # For random number generator

import logging                  # For loging errors.
# - - - - - - - - - - - - - - - - - - -

# -/- -/- -/-[ Files I made: ]-\- -\- -\-
import src.networking as networking
import config.config as config          # Config File - has all my constants/settings

import exporters.excel_exporter as excel_exporter
import exporters.csv_exporter as csv_exporter
import exporters.json_exporter as json_exporter
# -\- -\- -\- -\- -\- -/- -/- -/- -/- -/-

configJson = config.getConfigsFromJson()

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

# getUserInput - Gets the user input for how many pages the program will look through
# Parameters:
#       pageUrl - Used to figure out the total number of pages on the site
# Returns: The number of pages the user wants to scrape from. -1 If the user wants to quit 
# Error Handling: Doesn't Log. Raises informative exceptions
def getUserInput(pageUrl, session):
    soup = None
    # Get the soup of the page:
    try:
        soup = networking.getSoupRetry(pageUrl, session, configJson["numOfRetries"])
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

# generateFileOutputPath - Generates a file path to the folder where the output files will go.
# Parameters: None
# Returns: the folder path to the output folder as a string
# Error Handling: Logs errors. raises informative exception.
def generateFileOutputPath():
    folderPath = os.path.expanduser(configJson["outputFilePath"])
    
    # Create folder if it doesn't exist
    try:
        os.makedirs(folderPath, exist_ok=True)
    except Exception as e:
        logging.error(f"Failed to make directory to save output files. {e}")
        raise Exception("Failed to generate directory")
    
    return folderPath

# scrapePage - scrapes all the books from all the pages, and saves them to the 3 file formats
# Parameters:
#       pageUrl - the url of the current page. Will be incremented to go to next pages
#       session - the session it will use to pull data from the site
#       numOfPages - the number of pages it will scrape from
#       pageNum - keeping track of what page number we are on
#       workBook - for saving book data to excel
#       csvWriter - for saving book data to CSV file
#       jsonFile - for saving book data to JSON file
# Returns: Void, just saves the data of the current page, and then increments the page.
# Error Handling: Logs warnings internaly. Raises genaric exceptions.
def scrapePage(pageUrl, session, numOfPages, pageNum, workBook, csvWriter, jsonFile):
    # Loop through each page:
    for index in range(0, numOfPages):

        # Get the soup of the page:
        try:
            soup = networking.getSoupRetry(pageUrl, session, configJson["numOfRetries"])
        except Exception as e:
            # Log warning:
            logging.warning(f"Failed to get soup at page {pageNum}. {e}")
            print(f"\nCan not load page {pageNum}.\nCan not go further than page {pageNum - 1}.\nQuiting Program.")
            return

        # Get the books from the current page
        thisPage = networking.getBooksFromPage(soup)

        # If we got stuff from this page:
        if (thisPage != None):
            # Save this page to the different file formats:
            excel_exporter.savePageToWorkbook(workBook, thisPage, pageNum)
            csv_exporter.savePageToCSV(thisPage, csvWriter)
            json_exporter.savePageToJSON(thisPage, jsonFile)

            # Increment the page:
            pageUrl = networking.incrementPageUrlRetry(pageUrl, soup, session, pageNum)
                
            # Keep track of what page number we are on:
            pageNum += 1

            # And we update the loading bar:
            numOfEquals = int((configJson["lengthOfBar"]/numOfPages) * (index + 1))
            numOfDashes = configJson["lengthOfBar"] - numOfEquals
            print("|" + "="*numOfEquals + "-"*numOfDashes + "|  (" + str(index + 1) + " / " + str(numOfPages) + ")", end="\r")
        else:
            # Log error for when getBooksFromPage() returns none:
            logging.warning("Failed to get books from page " + str(index + 1) + ".")
        
        # Rate Limit:
        time.sleep(random.uniform(0.5, 1.5))

# scrapePages - scrapes all the books from all the pages it needs to
# Parameters:
#       numOfPages - the number of pages it will scrape from
#       session - the session it will use to pull data from the site
#       pageUrl - the url of the current page. Will be incremented to go to next pages
#       pageNum - keeping track of what page number we are on
#       workBook - for saving book data to excel
# Returns - Nothing, just saves stuff to the workBook
# Error Handling: Only logs info, doesn't raise exceptions
def scrapePages(numOfPages, session, pageUrl, pageNum, workBook, outputFolderPath):
    # Clear the terminal:
    os.system("clear")

    # Logging start of scraping procedure:
    logging.info(f"Starting to scrape {numOfPages} pages from {pageUrl}.")

    # Progress bar:
    print("Scraping from pages...")
    print("|" + "-"*configJson["lengthOfBar"] + "|  (0 / " + str(numOfPages) + ")", end="\r")

    # Open/make the csvFile:
    with open(csv_exporter.generateCsvFilePath(outputFolderPath), "w") as csvFile:
        
        # --/ --/ --[ CSV File stuff: ]-- \-- \--
        # Writer to write data to csv file:
        csvWriter = csv.writer(csvFile)
        # --\ --\ --\ --\ --\|/-- /-- /-- /-- /--

        # Open/make the jsonFile:
        with open(json_exporter.generateJsonFilePath(outputFolderPath), "w") as jsonFile:

            # Scrape all the book data we need from the page, and save it to the 3 file formats:
            scrapePage(pageUrl, session, numOfPages, pageNum, workBook, csvWriter, jsonFile)


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
    pageUrl = configJson["pageUrl"]             # The URL of the page we are currently on
    numOfPages = configJson["numOfPagesToScrape"]
    workBook = Workbook()                       # Workbook for saving the data into an excel doc
    pageNum = 1                                 # The page number of the page we are currently on
    # - - - - - - - - - - - - - - 
    
    # # Getting the user input:
    # try:
    #     numOfPages = getUserInput(pageUrl, session) # Gets user input for the number of pages to scrape data from
    # except Exception as e:
    #     # raising Exception:
    #     raise Exception(f"Failed to get user input. Quiting main. {e}")

    # If the number of pages is 0, then the user wants to exit the program:
    if (numOfPages == 0):
        logging.info("User is quiting the program")
        return

    # Find/Generate the output folder:
    try:
        outputFolderPath = generateFileOutputPath()
    except Exception as e:
        raise Exception(f"Failed to find/Generate folder for output files: {e}")

    # Try to scrape pages:
    try:
        scrapePages(numOfPages, session, pageUrl, pageNum, workBook, outputFolderPath)
    except Exception as e:
        # Raising exception:
        raise Exception(f"Failed to scape books: {e}")
    
    # Saving stuff:
    print("Saving output files to " + outputFolderPath)

    # Saving Excel
    try:
        excel_exporter.savingToExcelDoc(workBook, outputFolderPath)
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

# Wait a moment so the user can read the last ouput messages:
time.sleep(1.5)