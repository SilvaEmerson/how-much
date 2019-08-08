import os
import json

from src.scraping_demo import *


with open("./config.json", "r") as f:
    CONFIG = json.load(f)

PRICES_REGEXP =  {"magazine": r"(.+)\sà vista", "amazon": r"(.+)"}


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

    browser = launch_browser(f"{CONFIG['url']}{search_term}", options, CONFIG)

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
        on_completed=lambda: close_browser(browser),
    )

    base_obs.connect()
