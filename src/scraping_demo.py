from selenium import webdriver
from rx import operators as ops
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import rx

import re
import os


def launch_browser(url, options, config):
    browser = webdriver.Chrome(options=options)
    browser.get(url)
    delay = 3  # seconds

    try:
        myElem = WebDriverWait(browser, delay, 0.1).until(
            lambda brwoser: brwoser.find_element_by_xpath(
                config['xpath']["parent"]
            ).is_displayed()
        )
        print("Page is ready!")
    except TimeoutException:
        print("Loading took too much time!")

    return browser


def get_property(element, prop_xpath):
    prop = ""
    try:
        prop = element.find_element_by_xpath(f".{prop_xpath}").text
    except:
        pass

    return prop


def transform_price(product, regexp):
    new_price = re.findall(regexp, product["price"])[0]
    return {**product, "price": new_price}


def close_browser(browser):
    browser.close()
    browser.quit()
    try:
        os.system("killall chrome chromedriver")
    except:
        pass

