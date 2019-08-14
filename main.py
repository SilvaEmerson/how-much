from rx import Observable
from rx.scheduler import ThreadPoolScheduler

import os
import json

from src.operations import *


with open("./config.json", "r") as f:
    CONFIG = json.load(f)

if os.path.isfile('./cache.json'):
    with open("./cache.json", "r") as f:
        CACHE = json.load(f)
else:
    CACHE = [{}]

PRICES_REGEXP = {
    "magazine": r"(.+)\sà vista",
    "amazon": r"(.+)",
    "americanas": r"(.+)",
}


def main(search_term_input):
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

    found_products = shops.pipe(
        ops.zip(search_term),
        ops.subscribe_on(scheduler),
        ops.flat_map(lambda el: get_products(*el, options)),
        ops.publish(),
    )

    persist_prices_obs = found_products.pipe(
        ops.to_list(),
        ops.do_action(
            lambda products: persist_prices([{search_term_input: products}])
        ),
    )

    found_products.subscribe(on_next=print, on_error=lambda err: print(err))

    persist_prices_obs.subscribe()

    found_products.connect()


if __name__ == "__main__":
    search_term_input = input("> What your wish?\n> ").lower()

    if not search_term_input in list(CACHE[0].keys()):
        main(search_term_input)
    else:
        answer = input(
            f"{search_term_input} it's already at the cache, do you have look at?[Y/n]"
        ).lower()

        if answer == "y":
            rx.from_(CACHE[0][search_term_input]).subscribe(print).dispose()
        else:
            main(search_term_input)
