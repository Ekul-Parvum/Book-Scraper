import logging
import time
from bs4 import BeautifulSoup   # For formating the html data in a way that is nice to work with
import random
from urllib.parse import urljoin# Has some functions to make working with urls easy
from modules.book import Book

# region navigting the site Functions

# getSoup - Gets the soup for the given url
# Parameters:
#       string url - The url from which a soup will be got. I am a poet
#       session - This is used to get a repsonse from the site.
# Returns the soup - There are a TON of exceptions in here, so if this method runs successfully, you can trust it returns a functional soup
# Error Handling: Doesn't Log. Raises informative Exception.
def getSoup(url, session):
    try:
        response = session.get(url, timeout=10)
    except Exception as e:
        raise Exception("Failed to get Response from Session" + str(e))

    try:
        response.raise_for_status() # Raises an exception if it gets an unexpected status code like "404 Not Found"
    except Exception as e:
        raise Exception(f"Response Status flag: {e}")
    
    response.encoding = "utf-8"
    try:
        soup = BeautifulSoup(response.text, "html.parser")
    except Exception as e:
        raise Exception(f"Soup Failed: {e}")

    return soup

# getSoupRetry - Calls getSoup(), and if it fails, retries the given number of times
# Parameters:
#       string url - The url from which a soup will be got. I am a poet
#       session - This is used to get a repsonse from the site.
#       retryNum - The number of times the program is willing to retry getSoupRetry
# Returns the soup
# Error Handling: Logs Warnings internaly. Raises informative Exception.
def getSoupRetry(url, session, retryNum):
    for attempt in range(retryNum):
        try:
            return getSoup(url, session)
        except Exception as e:
            logging.warning(f"Attempt {attempt + 1}/{retryNum} to get soup of current page failed: {e}")
            time.sleep(random.uniform(0.5, 1.5))
    else:
        raise Exception(f"Failed to get soup after {retryNum} attempts. ")

# incrementPageUrl - changes the pageUrl based on the new pageNum
# Parameters:
#       currentUrl - The url we are currently on
# Returns string - The currentUrl with the given page num in it.
# Error Handling: Doesn't Log. Raises informative Exceptions.
def incrementPageUrl(currentUrl, soup):
    # find the link in the next button on the page. 
    nextButton = soup.find("li", class_="next")
    
    if (nextButton):
        nextPage = nextButton.find("a")["href"]
        nextUrl = urljoin(currentUrl, nextPage)
        return nextUrl
    else:
        raise Exception("Could not find Next Button with the next page URL")

# getNumberOfPages - Gets the number of pages of books in the website
# Parameters:
#       soup - The soup of the page it will search for the page num in
# Returns int - The number of pages. None if it failed to get a number
# Error Handling: Errors acounted for in return value
def getNumberOfPages(soup):
    # This will be the text in the <li> tag that has the page number
    pageOfText = soup.find("ul", class_="pager")

    if (pageOfText): # Checking that it found the <ul class="pager">
        pageOfText = pageOfText.find("li", class_="current")
        if (pageOfText): # Checking that it found the <li class="current">
            pageOfText = pageOfText.text
        else:
            return None # Return none of it could not find pageOfText
    else:
        return None # Return none of it could not find pageOfText
    
    # Assuming it found pageOfText, then we can start parsing it for the page number
    # The pageOfText should have something like "Page 1 of 50" or something.

    try:
        numOfPages = int(pageOfText.split()[-1])
        # This uses negative indexing, so yes, we are looking of the -1 index of the sequence.
        # That should be the last "word" in the pageOfText string, which should be the number of pages.
    except:
        return None
    
    if (numOfPages != -1):
        return numOfPages
    return None

# getBooksFromPage - Formats all the books in the given URL into book objects
# Paremeters:
#       soup - The soup of the page to be searched for books
# Returns: Array of books found at the given URL. Returns -1 if it failed. Returns none if no books were found.
# Error Handling: Errors acounted for in return value
def getBooksFromPage(soup):
    # Find all the books
    booksHtml = soup.find_all("article", class_="product_pod")

    # Books array:
    bookObjs = []

    for bookHtml in booksHtml:

        title_tag = bookHtml.select_one("h3 a")
        price_tag = bookHtml.select_one("p.price_color")

        # Checking that there is a title tag and price tag
        if (title_tag and price_tag):
            title = title_tag.get("title")
            # Note: tag["title"] would crash if there is no title, while .get("title") would return None

            # Checking that there is a title in the title_tag
            if (title):
                # Finaly, actualy puting the book data into a book object and into the bookObjs array
                bookObjs.append(
                    Book(
                        title,
                        price_tag.text
                    )
                )
    
    
    if (len(bookObjs) <= 0):
        return None
    
    return bookObjs
# endregion
