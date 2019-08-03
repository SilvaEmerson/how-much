from selenium import webdriver
from rx import operators as ops
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import rx

import json
import re


with open('./xpath_rules.json', 'r') as f:
    config = json.load(f)

URL = 'https://busca.magazineluiza.com.br/busca?q=notebook+acer&results_per_page=15'
prices_regexps = {
    'magazine': r'(.+)\sà vista'
}

config = config['magazine']
options = Options()
options.add_argument("--disable-extensions")
options.add_argument("--disable-gpu")
options.add_argument("disable-infobars") 

prefs={
    "profile.managed_default_content_settings.images": 2,
}

options.add_experimental_option("prefs", prefs)
options.headless = True
browser = webdriver.Chrome(options=options)
browser.get(URL)
delay = 3 # seconds

try:
    myElem = WebDriverWait(browser, delay, 0.1).until(lambda brwoser: brwoser.find_element_by_xpath(config['parent']).is_displayed())
    print("Page is ready!")
except TimeoutException:
    print("Loading took too much time!")

def get_products(element, parent=None, price=None, product_name=None):
    return (
            element.find_element_by_xpath(f'.{product_name}'),
            element.find_element_by_xpath(f'.{price}')
        )


def transform_price(product, regexp):
    new_price = re.findall(regexp,product['price'])[0]
    return {**product, 'price': new_price}


def close_browser():
    browser.close()
    browser.quit()

rx.of(browser).pipe(
    ops.flat_map(lambda browser: rx.from_(browser.find_elements_by_xpath(config['parent']))),
    ops.filter(lambda el: el.is_displayed()),
    ops.map(lambda el: get_products(el, **config)),
    ops.map(lambda product: { 'name': product[0].text, 'price': product[1].text }),
    ops.map(lambda product: transform_price(product, prices_regexps['magazine'])),
).subscribe(print, on_error=lambda err:print(err), on_completed=close_browser)

