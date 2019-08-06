from selenium import webdriver
from rx import operators as ops
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import rx

import json
import re
import os


with open("./config.json", "r") as f:
    CONFIG = json.load(f)

PRICES_REGEXP =  {"magazine": r"(.+)\sà vista", "amazon": r"(.+)"}


def launch_browser(url, options):
    browser = webdriver.Chrome(options=options)
    browser.get(url)
    delay = 3  # seconds

    try:
        myElem = WebDriverWait(browser, delay, 0.1).until(
            lambda brwoser: brwoser.find_element_by_xpath(
                CONFIG['xpath']["parent"]
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


def close_browser():
    browser.close()
    browser.quit()
    try:
        os.system("killall chrome chromedriver")
    except:
        pass


if __name__ == "__main__":
    CONFIG = CONFIG["magazine"]

    search_term_input = input("> What your wish?\n> ")
    search_term = CONFIG["innerChar"].join(search_term_input.split())

    options = Options()
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("disable-infobars")

    prefs = {"profile.managed_default_content_settings.images": 2}

    options.add_experimental_option("prefs", prefs)
    options.headless = True

    browser = launch_browser(f"{CONFIG['url']}{search_term}", options)

    base_obs = rx.of(browser).pipe(
        ops.flat_map(
            lambda browser: rx.from_(
                browser.find_elements_by_xpath(CONFIG["xpath"]["parent"])
            )
        ),
        ops.filter(lambda el: el.is_displayed()),
        ops.publish(),
    )

    prices = base_obs.pipe(
        ops.map(lambda el: get_property(el, CONFIG["xpath"]["price"]))
    )

    names = base_obs.pipe(
        ops.map(lambda el: get_property(el, CONFIG["xpath"]["product_name"]))
    )

    names.pipe(
        ops.zip(prices),
        ops.filter(lambda el: el[0] and el[1]),
        ops.map(lambda el: {"name": el[0], "price": el[1]}),
        ops.map(
            lambda product: transform_price(product, PRICES_REGEXP["amazon"])
        ),
    ).subscribe(
        on_next=print,
        on_error=lambda err: print(err),
        on_completed=close_browser,
    )

    base_obs.connect()
