import pandas as pd
def extractURLs_csv(csv, searchTerms, key, firstIndex, lastIndex):
    baseString = "https://www.google.com/search?q="
    
    # read in csv (maybe add value checks later)
    df = pd.read_csv(csv)
    
    # makes sure key is a list so it can be added to searchTerms
    if (not isinstance(key, list)):
        key = [key]
    
    search = df.loc[list(range(firstIndex,lastIndex+1)), searchTerms + key] # gets df with only search terms in desired rows
    
    search["url"] = baseString + search[searchTerms[0]] # column of base plus first search term
    # creates a column of url by adding on all other terms
    for s in searchTerms[1:]:
        search["url"] = search["url"] + "+" + search[s].astype(s)
        
    # converts key back into string
    key = key[0]
    
    # returns dictionary with key of key and value of url
    return dict(zip(list(search[key]),list(search["url"])))

import pandas as pd
import xlrd
def extractURLs_excel(xlsx, searchTerms, key, firstIndex, lastIndex):
    baseString = "https://www.google.com/search?q="
    
    # read in csv (maybe add value checks later)
    df = pd.read_excel(xlsx)
    
    # makes sure key is a list so it can be added to searchTerms
    if (not isinstance(key, list)):
        key = [key]
    
    search = df.loc[list(range(firstIndex,lastIndex+1)), searchTerms + key] # gets df with only search terms in desired rows
    
    search["url"] = baseString + search[searchTerms[0]] # column of base plus first search term
    # creates a column of url by adding on all other terms
    for s in searchTerms[1:]:
        search["url"] = search["url"] + "+" + search[s].astype(str)
        
    # converts key back into string
    key = key[0]
    
    # returns dictionary with key of key and value of url
    return dict(zip(list(search[key]),list(search["url"])))
    