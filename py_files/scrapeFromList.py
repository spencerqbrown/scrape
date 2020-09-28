import pandas as pd
from selenium.common.exceptions import NoSuchElementException
# note that this assumes scrolling has already occurred
def scrapeFromList(driver, key, name=True, stars=True, text=True, timeSince=True, openStatus=True):
    elements = driver.find_elements_by_xpath("//div[@class='gws-localreviews__general-reviews-block']//div[@class='WMbnJf gws-localreviews__google-review']")
    columnsBin = [name, stars, text, timeSince, openStatus]
    columnsNames = ["name", "stars", "text", "timeSince", "openStatus"]
    columnsPresent = [x for i, x in enumerate(columnsNames) if columnsBin[i]] # gets included columns
    print("preparing to scrape location with key", key)
    
    # text body
    textList = []
    if (text):
        textPath = ".//div[@style='vertical-align:top']//div[@class='Jtu6Td']//span[@jscontroller='P7L8k']"
        textPathFullExtension = "//span[@class='review-full-text']"
        textList = [0]*len(elements)
        i = 0
        for e in elements:
            try:
                textPartial = e.find_element_by_xpath(textPath+textPathFullExtension)
                e.find_element_by_xpath(textPath+"//span[@role='button']").click()
                textList[i] = e.find_element_by_xpath(textPath).text
            except NoSuchElementException:
                textList[i] = e.find_element_by_xpath(textPath).text
            i += 1
        
    # name
    nameList = []
    if (name):
        namePath = ".//div[@class='TSUbDb']"
        nameList = [e.find_element_by_xpath(namePath).text for e in elements]
    
    # stars
    starsList = []
    if (stars):
        starsPath = ".//div[@style='vertical-align:top']//div[@class='PuaHbe']//g-review-stars[@style='padding-right:7px']//span[@class='Fam1ne EBe2gf']"
        i = 0
        starsList = [0]*len(elements)
        for e in elements:
            raw = e.find_element_by_xpath(starsPath).get_attribute("aria-label")
            starCount = raw.split(" ")[1] # the number of stars
            starsList[i] = float(starCount)
            i += 1
    
    # timeSince
    timeSinceList = []
    if (timeSince):
        timeSincePath = ".//div[@style='vertical-align:top']//div[@class='PuaHbe']"
        timeSinceList = [e.find_element_by_xpath(timeSincePath).text for e in elements]
    
    # openStatus
    openStatusList = []
    if (openStatus):
        openStatusPath = "//div[@data-attrid='kc:/local:permanently closed']"
        if len(driver.find_elements_by_xpath(openStatusPath)) != 0:
            # if closed, this element will be found and list length will be nonzero
            openStatusList = ["Closed"]*len(elements)
        else:
            # if open, length of list of elements found will be 0
            openStatusList = ["Open"]*len(elements)

    # put df together
    columnsBin = [name, stars, text, timeSince, openStatus]
    columnsNames = ["name", "stars", "text", "timeSince", "openStatus"]
    columnsPresent = [x for i, x in enumerate(columnsNames) if columnsBin[i]] # gets included columns
    columns = [nameList, starsList, textList, timeSinceList, openStatusList]
    columns = [c for c in columns if len(c) > 0]
    data = {c:columns[i] for i,c in enumerate(columnsPresent)}
    df = pd.DataFrame(data)
    print("scraped location with key", key, "with", len(df), "reviews")
    
    return df