# Book scraper

    This is a Python web scrapper that collects book data from https://books.toscrape.com 
and exports the results into CSV(.csv), JSON(.json), and EXCEL(.xlsx).

    To run the file, simply double click the "BookScrapper" executable.

You can change the settings of the project in ./config/config.json.
Here is an explanation of all the settings you can change:
    outputFilePath - This is the path to the folder the output files will be saved to.
    outputFileName - This is the name of the output files, plus the file type. For example of the outputFileName was "George," then the csv file would be called "GeorgeCSV.csv"
    pageUrl - This is the url of the site the book scraper is collecting data from.
    numOfPagesToScrape - This is the number of pages from the site that the program will scrape.
    numOfRetries - If some page fails to load, or the scraper fails to collect necessary data, then this is how many times it will try again before giving up.
    lengthOfBar - this is the length of the loading bar displayed in the terminal.