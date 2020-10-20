from random import random
def randTime(low, high):
    val = random()
    time = low + (val  * (high - low))
    return time

import numbers
import time
def pauseScroll(wait):
    waitTime = 0
    # if argument is a list
    if (isinstance(wait, list)):
        # check if its length is valid
        if (len(wait) > 2) or (len(wait) < 1):
            raise ValueError
        # if length is valid get random number between vals
        low = wait[0]
        high = wait[1]
        # check for improper types, fix if possible
        if not isinstance(low, numbers.Number):
            if low.isnumeric():
                low = float(low)
            else:
                raise ValueError
        if not isinstance(high, numbers.Number):
            if high.isnumeric():
                high = float(high)
            else:
                raise ValueError
        waitTime = randTime(low, high)
    # if argument is a number
    elif (isinstance(wait, numbers.Number)):
        # get the number
        waitTime = wait
    # if argument is a string
    elif (isinstance(wait, str)):
        # if argument can be parsed as a number
        if (wait.isnumeric()):
            # get time as a number
            waitTime = float(wait)
        else:
            raise ValueError
    time.sleep(waitTime)

def getReviewTotal(driver):
    raw = driver.find_element_by_xpath("//span[@class='hqzQac']").text
    count = int(raw.split(" ")[0].replace(',',''))
    print("expecting", count, "reviews")
    return count

import time
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
def scrollDown(driver, reviewTotal, wait):
    x = len(driver.find_elements_by_xpath("//div[@class='gws-localreviews__general-reviews-block']//div[@class='WMbnJf gws-localreviews__google-review']"))
    lastx = x - 1
    repCount = 0
    print("scrolling...")
    # while we expect more reviews and we haven't repeated too much
    while ((x < reviewTotal) and (repCount < 10)):
        # pause to not look like a bot
        pauseScroll(wait)
        # select list of reviews
        elements = driver.find_elements_by_xpath("//div[@class='gws-localreviews__general-reviews-block']//div[@class='WMbnJf gws-localreviews__google-review']")
        # find the last visible review
        current_last = elements[-1]
        # check that there is not a response to the last review, else set that response as current_last
        owner_responses = driver.find_elements_by_xpath("//div[@class='LfKETd']")
        if (len(owner_responses) > 0):
            last_owner_response = owner_responses[-1]
            if last_owner_response.location['y'] > current_last.location['y']:
                current_last = last_owner_response
        # go to current last element
        current_last.location_once_scrolled_into_view
        # wait until page loads
        WebDriverWait(driver, 60).until(ec.invisibility_of_element_located((By.XPATH, "//div[@class='jfk-activityIndicator-icon']")))
        # take the previous review count and replace it with the new one
        lastx = x
        x = len(driver.find_elements_by_xpath("//div[@class='gws-localreviews__general-reviews-block']//div[@class='WMbnJf gws-localreviews__google-review']"))
        # if more reviews are not added to the visible reviews, mark repetition
        if (lastx == x):
            repCount += 1
        else:
            repCount = 0
            
    print("finished scrolling, found", x, "reviews")
    return x, reviewTotal