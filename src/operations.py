from selenium import webdriver
from rx import operators as ops
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from rx import Observable
import rx

import re
import os
from typing import Dict


COLORS = {"green": "\033[1;32;40m", "negative": "\033[3;37;40m", "underline": "\033[2;37;40m"}


def launch_browser(
    url: str, options: Options, config: Dict[str, str]
) -> webdriver:
    browser = webdriver.Chrome(options=options)
    browser.get(url)
    delay = 3  # seconds

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


def show_shops(config: Dict[str, dict]) -> None:
    shops = [*config.keys()]
    temp_str = map(
        lambda ind, shop: f"[{ind}] {shop}\r",
        range(len(shops)),
        shops,
    )
    return "\n".join(temp_str)


def get_products(
    shop: Dict[str, str], search_term: str, options
) -> Observable:
    browser = launch_browser(f"{shop['url']}{search_term}", options, shop)

    base_obs = rx.of(browser).pipe(
        ops.do_action(lambda el: print("Getting products price")),
        ops.flat_map(
            lambda browser: rx.from_(
                browser.find_elements_by_xpath(shop["xpath"]["parent"])
            )
        ),
        ops.filter(lambda el: el.is_displayed()),
        ops.map(
            lambda el: (
                get_property(el, shop["xpath"]["product_name"]),
                get_property(el, shop["xpath"]["price"]),
            )
        ),
        ops.filter(lambda el: el[0] and el[1]),
        ops.map(lambda el: {"name": el[0], "price": el[1]}),
        ops.map(lambda product: transform_price(product, shop["priceRegexp"])),
        ops.finally_action(lambda: browser.close()),
    )

    return base_obs
