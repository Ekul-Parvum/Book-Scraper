# Auther: Luke Smith
# Description: It scrapes data from https://books.toscrape.com and saves it into several file formats(only excel right now).

""" 
Improvements:
    1. Turn the Book object into a dataclass
    2. Stop using -1 for errors. Instead raise an exception
    3. Rather than storing all the pages, and then writing to the workbook, 
    scrape page -> write page to work book -> Then forget page and move on to next one.
    4. Rather than multiple sheets, just put some buffer rows between pages
    5. Loging instead of prints
    6. Pagination without building URLs - instead scrape the URL in the next button.
    7. CSV andn JSON exports as well
    8. Add Retrying, timeouts, and skiping - so that one page failing to load doesn't end 
    the whole program
    9. Figure out user angents so that sites don't block the scrape
    10. Rate limits - sending a but-ton of requests too quickly will make the target site raise flags
    11. Check for expected elements - if the site returns its own custom error page it could 
    break things as request.status_code wouldn't get that.
"""

import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook
from book import Book

print("Starting Program")

# incrementPageUrl - changes the pageUrl based on the new pageNum
# Parameters:
#       newPageNum - The new page number that the url should be updated to reflect
#       siteUrl - The base site url with out any page number
# Returns string - The siteUrl with the given page num in it.
def incrementPageUrl(newPageNum, siteUrl):
    return siteUrl + str(newPageNum) + ".html"

# getSoup - Gets the soup for the given url
# Parameters:
#       string url - The url from which a soup will be got. I am a poet
# Returns the soup, or -1 if something went wrong
def getSoup(url):
    try:
        response = requests.get(url)
    except requests.exceptions.MissingSchema:
        print("Invalid URL (missing schema, like http://)")
        return -1
    except requests.exceptions.InvalidURL:
        print("Invalid URL format")
        return -1
    except requests.exceptions.ConnectionError:
        print("Failed to connect to server")
        return -1
    except requests.exceptions.Timeout:
        print("Request timed out")
        return -1
    except requests.exceptions.RequestException as e:
        print("Other request error:", e)
        return -1

    code = response.status_code
    match code:
        case _ if 100 <= code <= 199:
            print("[" + str(code) + "]: Informational")
            return -1
        case _ if 200 <= code <= 299:
            pass
        case _ if 300 <= code <= 399:
            print("[" + str(code) + "]: Redirected from site")
            return -1
        case _ if 400 <= code <= 499:
            print("[" + str(code) + "]: Client Error")
            return -1
        case _ if 500 <= code <= 599:
            print("[" + str(code) + "]: Server Error")
            return -1
        case _:
            try:
                codeStr = str(code)
                print("Encountered Unkown status Code: " + codeStr)
            except:
                print("Encountered Unkown status Code.")
            return -1


    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")
    return soup

# getNumberOfPages - Gets the number of pages of books in the website
# Parameters:
#       url - The url it will search for the page num in
# Returns int - The number of pages. Negative 1 if it failed to get a number
def getNumberOfPages(url):
    soup = getSoup(url)

    if (soup == -1):
        return -1

    pageOfText = soup.find("ul", class_="pager").find("li", class_="current").text
    start = int(pageOfText.rfind("of")) + 3
    end = pageOfText.find(" ", start)

    numOfPages = -1

    if (end != -1):
        try:
            numOfPages = int(pageOfText[start:end])
        except ValueError:
            print("Error: Invalid Page Number. Could not convert " + pageOfText[start:end] + " to int.")

    return numOfPages

# printBooks - Prints all the books in the given array of books
# Paremeters:
#       bookObjs - Array of books to print
# Returns nothing
def printBooks(bookObjs):
    for book in bookObjs:
        print("----------------------")
        print("Title: " + book.title)
        print("Price: " + book.price)
    print("----------------------")

# getBooksFromPage - Formats all the books in the given URL into book objects
# Paremeters:
#       pageUrl - string with the url of the page to be searched for books
# Returns: Array of books found at the given URL. Returns -1 if it failed
def getBooksFromPage(pageUrl):
    soup = getSoup(pageUrl)

    if (soup == -1):
        return -1

    # Find all the books
    booksHtml = soup.find_all("article", class_="product_pod")

    # Books array:
    bookObjs = []

    for bookHtml in booksHtml:
        bookObjs.append(
            Book(
                bookHtml.h3.a["title"],
                bookHtml.find("p", class_="price_color").text
            )
        )
    
    return bookObjs

# makeWorkBookSheet - Compiles all the given book objects into an excel sheet
# Parameters:
#       bookObjs - Array of all the book objects to put into the exvel sheet
#       pageNum - The page number the books are from, and the page this excel sheet will be
#       sheet - The sheet object that the bookObjs will be put into.
# Returns: Nothing
def makeWorkBookSheet(bookObjs, pageNum, sheet):
    # Making the sheet:
    sheet.title = "Books, page " + str(pageNum)

    # Making a header:
    sheet.append(["Title", "Price"])

    # Looping through each book:
    for book in bookObjs:
        sheet.append(book.getRowOfData())

# getUserInput - Gets the user input for how many pages the program will look through
# Parameters: None
# Returns: The number of pages the user wants to scrape from. 0 If the user wants to quit 
def getUserInput():
    numOfPages = getNumberOfPages(pageUrl)

    if (numOfPages < 0):
        print("Failed to get Pages. Quiting Program")
        return 0

    print("Total Number of pages: " + str(numOfPages))

    userInput = -1
    while (userInput < 0 or userInput > numOfPages):
        print("\nInput 0 to leave the program")
        userInput = input("How many pages do you want to scrape?: ")
        try:
            userInput = int(userInput)
            if (userInput < 0 or userInput > numOfPages):
                print("That number is out of range. Please try again")
        except:
            print("That is not a valid number. Please try again")
            userInput = -1

    return userInput


siteUrl = "https://books.toscrape.com/catalogue/page-"
pageNum = 1
pageUrl = siteUrl + str(pageNum) + ".html"

pages = []
lengthOfBar = 30

numOfPages = getUserInput()

if (numOfPages != 0):
    print("Scraping from pages.")
    print("|" + "-"*lengthOfBar + "|  (0 / " + str(numOfPages) + ")", end="\r")

    for index in range(0, numOfPages):
        thisPage = getBooksFromPage(pageUrl)
        if (thisPage != -1):
            pages.append(thisPage)
            pageNum += 1
            pageUrl = incrementPageUrl(pageNum, siteUrl)

            numOfEquals = int((lengthOfBar/numOfPages) * (index + 1))
            numOfDashes = lengthOfBar - numOfEquals
            print("|" + "="*numOfEquals + "-"*numOfDashes + "|  (" + str(index + 1) + " / " + str(numOfPages) + ")", end="\r")
        else:
            print("Failed to get books from page " + str(index + 1) + ".")

    print("\n")

    print("Making Excel Object")
    workBook = Workbook()
    sheet = workBook.active

    print("Pushing Data into Excel Object")
    for pageNumber, page in enumerate(pages, start=1):
        makeWorkBookSheet(page, pageNumber, sheet)
        if (pageNumber < numOfPages):
            sheet = workBook.create_sheet(title="New Sheet")

    print("Saving Excel Document")
    workBook.save("TrialRun.xlsx")

print("Thank you for using this program!")