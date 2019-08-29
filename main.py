#! /usr/bin/python3

from rx import operators as ops
from rx.scheduler import ThreadPoolScheduler
from selenium.webdriver.chrome.options import Options
import rx

import os
import json
import re

from src.operations import (
    show_shops,
    persist_prices,
    get_products,
    shop_picker_input,
    persist_prices_obs,
    search_product
)


with open("./config.json", "r") as f:
    CONFIG = json.load(f)

if os.path.isfile("./cache.json"):
    with open("./cache.json", "r") as f:
        CACHE = json.load(f)
else:
    CACHE = [{}]


def main(found_products_obs):
    shops_input = shop_picker_input(shops_picker_msg)
    shops_list = shops_input.split(",")

    found_products = search_product(search_term_input, shops_list).pipe(
        ops.subscribe_on(scheduler)
    )
    persist_prices_obs = persist_prices_obs(found_products_obs)
    found_products_subscription = found_products.subscribe(
        on_next=print,
        on_error=lambda err: print(err),
        on_completed=lambda: found_products_subscription.dispose(),
    )
    persist_prices_subscription = persist_prices_obs.subscribe(
        on_completed=lambda: persist_prices_subscription.dispose()
    )
    found_products.connect()


if __name__ == "__main__":
    subscription = None

    scheduler = ThreadPoolScheduler(len(shops_list))

    search_term_input = input("> What your wish?\n> ").lower()

    if not search_term_input in list(CACHE[0].keys()):
        shops_input = shop_picker_input(shops_picker_msg)
        shops_list = shops_input.split(",")

        found_products = main(search_term_input, shops_list).pipe(
            ops.subscribe_on(scheduler)
        )
        persist_prices_obs = persist_prices_obs(found_products)
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
            shops_input = shop_picker_input(shops_picker_msg)
            shops_list = shops_input.split(",")

            found_products = main(search_term_input, shop_picker_input).pipe(
                ops.subscribe_on(scheduler)
            )
            persist_prices_obs = persist_prices_obs(found_products)
            found_products_subscription = found_products.subscribe(
                on_next=print,
                on_error=lambda err: print(err),
                on_completed=lambda: found_products_subscription.dispose(),
            )
            persist_prices_subscription = persist_prices_obs.subscribe(
                on_completed=lambda: persist_prices_subscription.dispose()
            )
            found_products.connect()
