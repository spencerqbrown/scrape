import openpyxl
import pandas as pd
from extractors import extractURLs_csv
from extractors import extractURLs_excel
from scrapeFromURLs import scrapeFromURLs
def simpleScraper(sourceFile, searchTerms, key, firstIndex, lastIndex, wait=[2,3], combine=True, statusCol=None, overWrite=False):
    
    # get url dict
    ext = sourceFile.split(".")[-1] # file extension
    urls = {}
    if (ext == "xlsx"):
        urls = extractURLs_excel(sourceFile, searchTerms, key, firstIndex, lastIndex)
    elif (ext == "csv"):
        urls = extractURLs_csv(sourceFile, searchTerms, key, firstIndex, lastIndex)
    else:
        raise ValueError
    
    # scrape and save
    status = scrapeFromURLs(urls, combine, wait)
    
    # mark source file
    if statusCol is not None:
        if (ext == "xlsx"):
            source = pd.read_excel(sourceFile)
        elif (ext == "csv"):
            source = pd.read_csv(sourceFile)
        else:
            raise ValueError
        # make status list and put into source file df
        status_final = ["Scraped" if s is 1 else "Failed" for s in status]
        source.loc[firstIndex:lastIndex,[statusCol]] = status_final
        if overWrite:
            if (ext == "xlsx"):
                source.to_excel(sourceFile, index=False)
            elif (ext == "csv"):
                source.to_csv(sourceFile, index=False)
            else:
                raise ValueError
        else:
            if (ext == "xlsx"):
                source.to_excel(sourceFile.split('.')[0]+'_.'+ext, index=False)
            elif (ext == "csv"):
                source.to_csv(sourceFile.split('.')[0]+'_.'+ext, index=False)
            else:
                raise ValueError
            