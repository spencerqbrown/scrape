import datetime
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from scroll import scrollDown,getReviewTotal
from scrapeFromList import scrapeFromList
from selenium.webdriver.common.action_chains import ActionChains
import os
import logging
import traceback
def scrapeFromURLs(urls, checkAddress=True, combine=True, wait=[2,3], filePath="", alternate=False, limit=None, firefox=False):
    log_file_name = "logfile_"+str(datetime.datetime.now()).replace(' ','_').replace(':','_').replace('.','_')+".log"
    logging.basicConfig(filename=log_file_name, level=logging.WARNING)
    print("combine:",combine)
    print("wait:",wait)

    # fix filePath if necessary
    if (filePath[-2:] != "\\"):
        filePath = filePath + "\\"
    # note that the above will probably not fix a case with a single slash

    # check that urls are dicts
    if not (isinstance(urls, dict)):
        raise ValueError

    # chrome options config
    if not firefox:
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
    # start selenium stuff
    if not firefox:
        driver = webdriver.Chrome('./chromedriver', chrome_options=chrome_options)
    else:
        gecko_abs_path = os.path.abspath('./geckodriver')
        driver = webdriver.Firefox(executable_path=gecko_abs_path)
    print(driver.title)
    
    dfs = [0]*len(urls)

    # if alternate method, go to google base page temporarily
    if alternate:
        driver.get("https://www.google.com/search?q=a")
    
    # for each id
    r_count = 0
    i = 0
    status = [0]*len(urls)
    for id in urls:
        
        # go to url
        # if alternate use previous page as basis and do a google search from there
        url = urls.get(id)
        if alternate:
            url_terms = " ".join(url.split("=")[1].split("+"))
            search_box = driver.find_element_by_xpath("//input[@aria-label='Search']")
            search_box.clear()
            print("Seaching: " + url_terms)
            search_box.send_keys(url_terms)
            search_box.send_keys(Keys.ENTER)
        # if not alternate, go straight to url
        else:
            driver.get(url)
        
        # check that address is correct
        # note this will assume the second url parameter is address number, last is state, second to last is town
        if checkAddress:
            parameters = url.split('=')[1].split('+') # gets the url parameters after the '=' in a list
            addr_number = parameters[1].split(' ')[0] # gets the address number
            town = parameters[-2].lower() # gets the town
            state = parameters[-1].lower() # gets the state
            addr = driver.find_elements_by_xpath("//span[@class='LrzXr']") # gets the found address as list
            if (len(addr) != 0):
                # found address
                addr = addr[0].text.split(',') # set address to first element of address found
                found_addr_number = addr[0].split(' ')[0]
                # sometimes a highway or something is the second element, check length of address
                standardLength = 3
                if (len(addr) > standardLength):
                    found_town = addr[2].lstrip(' ').lower()
                else:
                    found_town = addr[1].lstrip(' ').lower()
                found_state = addr[-1].lstrip(' ').split(' ')[0].lower()
                # if a check is not met, do not scrape the location, i.e. put a blank df in its final place and do not mark as done
                if found_addr_number != addr_number:
                    dfs[i] = pd.DataFrame({})
                    i += 1
                    print("failed to scrape location with key",id,"due to unmatched address number, continuing...")
                    logString = "failed to scrape location with key " + str(id) + " due to unmatched address. Expected " + str(addr_number) + ", but found " + str(found_addr_number)
                    logging.warning(logString)
                    continue
                elif found_town != town:
                    dfs[i] = pd.DataFrame({})
                    i += 1
                    print("failed to scrape location with key",id,"due to unmatched town, continuing...")
                    print("expected town:",town,"-found town:",found_town)
                    logString = "failed to scrape location with key " + str(id) + " due to unmatched town. Expected " + town + ", but found " + found_town
                    logging.warning(logString)
                    continue
                elif found_state != state:
                    dfs[i] = pd.DataFrame({})
                    i += 1
                    print("failed to scrape location with key",id,"due to unmatched state, continuing...")
                    logString = "failed to scrape location with key " + str(id) + " due to unmatched state. Expected " + state + ", but found " + found_state
                    logging.warning(logString)
                    continue
            else:
                # if location address is not found, move on
                dfs[i] = pd.DataFrame({})
                i += 1
                print("failed to scrape location with key",id,"due to unlisted location, continuing...")
                logString = "Failed to scrape location with key " + str(id) + " due to unlisted location."
                logging.warning(logString)
                continue
        


        review_block_class = "gws-localreviews__general-reviews-block"
        review_class = "WMbnJf vY6njf gws-localreviews__google-review" 
        reloads = 0
        keep_going = True
        while (keep_going):
            button = driver.find_elements_by_class_name("hqzQac")
            if (len(button) > 0):
                # button found
                distance_to_scroll = driver.get_window_size()["width"]
                driver.execute_script("window.scrollBy(" + str(distance_to_scroll) + ", 0)")
                ActionChains(driver).move_to_element(button[0]).click().perform()
                keep_going = False
            else:
                # no button found
                # try to reload
                try:
                    WebDriverWait(driver, 15).until(ec.presence_of_element_located((By.XPATH, "//div[@class='" + review_block_class + "']//div[@class='" + review_class + "']")))
                except TimeoutException:
                    if alternate:
                        url_terms = " ".join(url.split("=")[1].split("+"))
                        search_box = driver.find_element_by_xpath("//input[@aria-label='Search']")
                        search_box.clear()
                        print("Seaching: " + url_terms)
                        search_box.send_keys(url_terms)
                        search_box.send_keys(Keys.ENTER)
                    else:
                        driver.get(url)
                    reloads += 1
                    if reloads >= 5:
                        keep_going = False
        if (reloads >= 5):
            # no button found
            dfs[i] = pd.DataFrame({})
            i += 1
            print("failed to scrape location with key",id,"due to missing button, continuing...")
            continue
        
        # scroll to bottom
        percent_reviews_found = 0
        repCount = 0
        reviewTotal = 11
        tempRevTotal = getReviewTotal(driver)
        # check for overly large review total
        if (limit != None) and (tempRevTotal > limit):
            logString = "Failed to scrape location with key " + str(id) + ". Too many reviews: " + str(tempRevTotal)
            print(logString)
            logging.warning(logString)
            dfs[i] = pd.DataFrame({})
            i += 1
            continue
        # get at least 95% of reviews at location
        while (percent_reviews_found < 0.95) and (reviewTotal >= 11):
            reviewTotal = tempRevTotal
            print(reviewTotal)
            x = scrollDown(driver, reviewTotal, wait)
            print(x)
            percent_reviews_found = x / reviewTotal
            print("Found",percent_reviews_found*100,"% of reviews for this location.")
            if percent_reviews_found < 0.95:
                # scroll up slightly
                driver.execute_script("window.scrollBy(0, -50)")
                print("trying to scroll again...")
            else:
                print("found most reviews, moving on...")
            repCount += 1
            # stop trying after 10 repetitions
            if repCount > 10:
                logString = "Failed to scroll all reviews for location with key " + str(id) + ". Found only " + str(x) + " reviews out of " + str(reviewTotal)
                logging.warning(logString)
                break
            
        # if scrolling fails, skip location
        if (repCount > 10):
            dfs[i] = pd.DataFrame({})
            i += 1
            print("failed to scrape location with key",id," due to scrolling failure, continuing...")
            traceback.print_exc()
            logString = "failed to scrape location with key " + str(id) + " due to scrolling failure."
            logging.warning(logString)
            continue
        
        # scrape from loaded list
        # if a scrape fails, move onto the next one
        try:
            df = scrapeFromList(driver, id)
        except:
            dfs[i] = pd.DataFrame({})
            i += 1
            print("failed to scrape location with key",id,", continuing...")
            traceback.print_exc()
            logString = "failed to scrape location with key " + str(id) + " for unknown reason."
            logging.warning(logString)
            continue
        df["key"] = str(id)
        
        dfs[i] = df

        # output the df if not combining
        if (not combine):
            print("saving location with key",id)
            outstr = "scraped_"+str(datetime.datetime.now()).replace(' ','_').replace(':','_').replace('.','_')+".csv"
            df.to_csv(filePath+outstr,index=False)
            print("saved location with key", id, "as", outstr)
        
        r_count += len(df)
        status[i] = 1
        i += 1
        
    # combine dfs if necessary
    if (combine):
        df = dfs[0]
        # append all other dfs to the first one, then save to csv
        for i in dfs[1:]:
            df = df.append(i, ignore_index=True)
        fName = "combined_scrape_"+str(datetime.datetime.now()).replace(' ','_').replace(':','_').replace('.','_')+".csv"
        df.to_csv(filePath+fName,index=False)
        
    # for testing if rows are lost
    print("sum of all rows:",r_count)
    
    driver.quit()
    
    return status