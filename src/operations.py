from selenium import webdriver
from rx import Observable
from rx import operators as ops
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
import rx

import re
import os
import json
from typing import Dict


COLORS = {
    "green": "\033[1;32;40m",
    "negative": "\033[3;37;40m",
    "underline": "\033[2;37;40m",
}


PRICES_REGEXP = {
    "magazine": r"(.+)\sà vista",
    "amazon": r"(.+)",
    "americanas": r"(.+)",
}


def search_product(
    search_term_input, shops_list, shops_picker_msg, CONFIG=None
):
    shops_picker_msg = show_shops(CONFIG)

    options = Options()
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-infobars")

    prefs = {"profile.managed_default_content_settings.images": 2}

    options.add_experimental_option("prefs", prefs)
    options.headless = True

    shops = rx.from_(shops_list).pipe(
        ops.map(
            lambda shop: re.findall(f"\[{shop}\]\s(\w+)", shops_picker_msg)[0]
        ),
        ops.map(
            lambda shop: {
                **CONFIG.get(shop),
                "priceRegexp": PRICES_REGEXP.get(shop),
            }
        ),
        ops.filter(lambda el: el),
    )

    search_term = shops.pipe(
        ops.pluck("innerChar"),
        ops.map(lambda inner_char: inner_char.join(search_term_input.split())),
    )

    found_products = shops.pipe(
        ops.zip(search_term),
        ops.flat_map(lambda el: get_products(*el, options)),
        ops.publish(),
    )

    return found_products


def persist_prices_obs(found_products_obs):
    persist_prices_obs = found_products_obs.pipe(
        ops.to_list(),
        ops.do_action(
            lambda products: persist_prices([{search_term_input: products}])
        ),
    )
    return persist_prices_obs


def shop_picker_input(shops_picker_msg):
    return input(
        f"> Choose what shop(s) you want to search by typing the respective number(s):\n{shops_picker_msg}\n>> "
    )


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
        lambda ind, shop: f"[{ind}] {shop}", range(len(shops)), shops
    )
    return "\n".join(temp_str)


def persist_prices(prices):
    with open("./cache.json", "w") as f:
        json.dump(prices, f)


def get_products(
    shop: Dict[str, str], search_term: str, options
) -> Observable:
    domain = re.findall("\.(.+)\.com", shop["url"])[0]
    print(f"Lauching {domain}")

    browser = launch_browser(f"{shop['url']}{search_term}", options, shop)

    base_obs = rx.of(browser).pipe(
        ops.do_action(
            lambda el: print(f"Getting products prices from {domain}")
        ),
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
