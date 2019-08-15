from rx import operators as ops
from rx.scheduler import ThreadPoolScheduler
from selenium.webdriver.chrome.options import Options
import rx

import os
import json
import re

from src.operations import show_shops, persist_prices, get_products


with open("./config.json", "r") as f:
    CONFIG = json.load(f)

if os.path.isfile("./cache.json"):
    with open("./cache.json", "r") as f:
        CACHE = json.load(f)
else:
    CACHE = [{}]

PRICES_REGEXP = {
    "magazine": r"(.+)\sà vista",
    "amazon": r"(.+)",
    "americanas": r"(.+)",
}


def shop_picker_input():
    return input(
        f"> Choose what shop(s) you want to search by typing the respective number(s):\n{shops_picker}\n>> "
    )


def main(search_term_input, shop_picker_input):
    shops_picker = show_shops(CONFIG)
    shops_input = shop_picker_input()

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

    return found_products


def persist_prices(found_products_obs):
    persist_prices_obs = found_products.pipe(
        ops.to_list(),
        ops.do_action(
            lambda products: persist_prices([{search_term_input: products}])
        ),
    )
    return persist_prices_obs


if __name__ == "__main__":
    subscription = None

    search_term_input = input("> What your wish?\n> ").lower()

    if not search_term_input in list(CACHE[0].keys()):
        found_products = main(search_term_input, shop_picker_input)
        persist_prices_obs = persist_prices(found_products)
        found_products_subscription = found_products.subscribe(
            on_next=print,
            on_error=lambda err: print(err),
            on_completed=lambda: found_products_subscription.dispose(),
        )
        persist_prices_subscription = persist_prices_obs.subscribe(
            on_completed=lambda: persist_prices_subscription.dispose()
        )
        found_products.connect()
    else:
        answer = input(
            f"{search_term_input} it's already at the cache, do you have look at?[Y/n]"
        ).lower()

        if answer == "y":
            rx.from_(CACHE[0][search_term_input]).subscribe(print).dispose()
        else:
            found_products = main(search_term_input, shop_picker_input)
            persist_prices_obs = persist_prices(found_products)
            found_products_subscription = found_products.subscribe(
                on_next=print,
                on_error=lambda err: print(err),
                on_completed=lambda: found_products_subscription.dispose(),
            )
            persist_prices_subscription = persist_prices_obs.subscribe(
                on_completed=lambda: persist_prices_subscription.dispose()
            )
            found_products.connect()
