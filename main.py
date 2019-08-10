from rx import Observable
from rx.scheduler import ThreadPoolScheduler

import os
import json

from src.operations import *


with open("./config.json", "r") as f:
    CONFIG = json.load(f)

PRICES_REGEXP = {"magazine": r"(.+)\sà vista", "amazon": r"(.+)"}


if __name__ == "__main__":
    search_term_input = input("> What your wish?\n> ")

    shops_picker = show_shops(CONFIG)
    shops_input = input(
        f"> Choose what shop(s) you want to search by typing the respective number(s):\n{shops_picker}\n>> "
    )

    options = Options()
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-infobars")

    prefs = {"profile.managed_default_content_settings.images": 2}

    options.add_experimental_option("prefs", prefs)
    options.headless = True

    shops_list = shops_input.split(",")

    scheduler = ThreadPoolScheduler(len(shops_list))

    shops = rx.from_(shops_list).pipe(
        ops.map(
            lambda shop: re.findall(f"\[{shop}\]\s(\w+)", shops_picker)[0]
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

    shops.pipe(
        ops.zip(search_term),
        ops.subscribe_on(scheduler),
        ops.flat_map(lambda el: get_products(*el, options)),
    ).subscribe(
        on_next=print,
        on_error=lambda err: print(err),
    )
