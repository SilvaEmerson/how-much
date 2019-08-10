from selenium import webdriver
from rx import operators as ops
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import rx

import re
import os
from typing import Dict


def launch_browser(url: str, options: Options, config: Dict[str, str]) -> webdriver:
    browser = webdriver.Chrome(options=options)
    browser.get(url)
    delay = 2  # seconds

    try:
        myElem = WebDriverWait(browser, delay, 0.1).until(
            lambda brwoser: brwoser.find_element_by_xpath(
                config["xpath"]["parent"]
            ).is_displayed()
        )
        print("Page is ready!")
    except TimeoutException:
        print("Loading took too much time!")

    return browser


def get_property(element: webdriver, prop_xpath: str) -> str:
    prop = ""
    try:
        prop = element.find_element_by_xpath(f".{prop_xpath}").text
    except:
        pass

    return prop


def transform_price(product: Dict[str, str], regexp: str) -> Dict[str, str]:
    new_price = re.findall(regexp, product["price"])[0]
    return {**product, "price": new_price}


def close_browser(browser: webdriver) -> None:
    browser.close()
    browser.quit()
    try:
        os.system("killall chrome chromedriver")
    except:
        pass

def show_shops(config: Dict[str, dict]) -> None:
    shops = [*config.keys()]
    temp_str = map(lambda ind, shop: f'[{ind}] {shop}', range(len(shops)), shops)
    return '\n'.join(temp_str)
