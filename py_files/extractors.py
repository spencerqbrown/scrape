import pandas as pd
import xlrd
def extractURLs(sourceFile, searchTerms, key, indices):

    # read in file
    ext = sourceFile.split(".")[-1] # file extension
    if (ext == "xlsx"):
        df = pd.read_excel(sourceFile)
    elif (ext == "csv"):
        df = pd.read_csv(sourceFile)
    else:
        raise ValueError

    baseString = "https://www.google.com/search?q="
    
    # makes sure key is a list so it can be added to searchTerms
    if (not isinstance(key, list)):
        key = [key]
    
    search = df.loc[indices, searchTerms + key] # gets df with only search terms in desired rows
    
    search["url"] = baseString + search[searchTerms[0]] # column of base plus first search term
    # creates a column of url by adding on all other terms
    for s in searchTerms[1:]:
        search["url"] = search["url"] + "+" + search[s].astype(str)
        
    # converts key back into string
    key = key[0]
    
    # returns dictionary with key of key and value of url
    return dict(zip(list(search[key]),list(search["url"])))
    