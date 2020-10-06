import openpyxl
import numpy as np
import pandas as pd
from extractors import extractURLs
from scrapeFromURLs import scrapeFromURLs
def simpleScraper(sourceFile, searchTerms, key, indices, wait=[2,3], combine=True, statusCol=None, overWrite=False, checkAddress=True, filePath=""):
    
    # get url dict
    ext = sourceFile.split(".")[-1] # file extension
    urls = extractURLs(sourceFile, searchTerms, key, indices)
    
    # scrape and save
    status = scrapeFromURLs(urls=urls, checkAddress=checkAddress, combine=combine, wait=wait, filePath=filePath)
    
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
        status_final = np.reshape(status_final, (len(status_final),1))
        source.loc[indices,[statusCol]] = status_final
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
            