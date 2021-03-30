# Other libs
import time
from bs4 import BeautifulSoup as bs
from random import randint
from gevent import monkey

# Monkey library debug
def stub(*args, **kwargs):  # pylint: disable=unused-argument
    pass
monkey.patch_all = stub

# Web scraping required libs
import windscribe
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests_futures.sessions import FuturesSession

import json

# Program execution count
loop_count = 0

# Connect to windscribe
print("Connecting to Windscribe...")
windscribe.connect(rand=True)

DOMAIN = 'amazon'

# TELEGRAM BOT API
CHAT_ID = "__TELEGRAM_CHAT_ID__"
TOKEN = "__TELEGRAM_TOKEN__"
TELEGRAM_API_SEND_MSG = f'https://api.telegram.org/bot{TOKEN}/sendMessage'

TOKEN2 = "__TELEGRAM_TOKEN__"
TELEGRAM_API_SEND_MSG2 = f'https://api.telegram.org/bot{TOKEN2}/sendMessage'
BOTSTATUS_ID = "__TELEGRAM_CHAT_ID__"

# Request input settings
INPUT_FILE = "products.json"
REQUEST_PER_CALL = 8

# User agents
headers = [
    {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36', 'Cache-Control': 'no-cache', "Pragma": "no-cache"},
    {"User-Agent": 'Mozilla/5.0 (Linux; U; Android 2.2) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1', 'Cache-Control': 'no-cache', "Pragma": "no-cache"},
    {"User-Agent": 'Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko; googleweblight) Chrome/38.0.1025.166 Mobile Safari/535.19', 'Cache-Control': 'no-cache', "Pragma": "no-cache"},
    {"User-Agent": 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148', 'Cache-Control': 'no-cache', "Pragma": "no-cache"},
    {"User-Agent": 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_1_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16D57', 'Cache-Control': 'no-cache', "Pragma": "no-cache"},
    {"User-Agent": 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1 Mobile/15E148 Safari/604.1', 'Cache-Control': 'no-cache', "Pragma": "no-cache"},
    {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36', 'Cache-Control': 'no-cache', "Pragma": "no-cache"},
    {"User-Agent": 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)', 'Cache-Control': 'no-cache', "Pragma": "no-cache"},
    {"User-Agent": 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36', 'Cache-Control': 'no-cache', "Pragma": "no-cache"},
    {"User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8', 'Cache-Control': 'no-cache', "Pragma": "no-cache"},
    {"User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/601.7.8 (KHTML, like Gecko)', 'Cache-Control': 'no-cache', "Pragma": "no-cache"},
    {"User-Agent": 'Mozilla/5.0 (Linux; Android 6.0; CAM-L21 Build/HUAWEICAM-L21; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/62.0.3202.84 Mobile Safari/537.36', 'Cache-Control': 'no-cache', "Pragma": "no-cache"},
    {"User-Agent": 'Mozilla/5.0 (Linux; Android 8.0.0; WAS-LX3 Build/HUAWEIWAS-LX3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Mobile Safari/537.36', 'Cache-Control': 'no-cache', "Pragma": "no-cache"},
    {"User-Agent": 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 [FBAN/FBIOS;FBDV/iPhone8,1;FBMD/iPhone;FBSN/iOS;FBSV/13.4.1;FBSS/2;FBID/phone;FBLC/en_US;FBOP/5]', 'Cache-Control': 'no-cache', "Pragma": "no-cache"},
    {"User-Agent": 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 [FBAN/FBIOS;FBDV/iPhone9,3;FBMD/iPhone;FBSN/iOS;FBSV/13.3.1;FBSS/2;FBID/phone;FBLC/en_US;FBOP/5;FBCR/]', 'Cache-Control': 'no-cache', "Pragma": "no-cache"},
    {"User-Agent": 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 [FBAN/FBIOS;FBDV/iPhone9,2;FBMD/iPhone;FBSN/iOS;FBSV/13.3.1;FBSS/3;FBID/phone;FBLC/en_US;FBOP/5;FBCR/]', 'Cache-Control': 'no-cache', "Pragma": "no-cache"}
]

# Product URLs
product_urls = []
i = 0
# Read json file
with open(INPUT_FILE, 'r') as PRODUCTS_JSON:
    data = json.load(PRODUCTS_JSON)
    all_products = data["products"]

    for el in all_products:
        product_urls.append(el["url"])

        i += 1

# Async Request session
session = FuturesSession(executor=ThreadPoolExecutor(max_workers=REQUEST_PER_CALL), session=requests.Session())

# All requests
reqs = []

# Get the request URL's and make the requests
for url in product_urls:

    nation = url[url.find(DOMAIN)+len(DOMAIN):url.rfind('/dp')]

    if (len(nation) > 7):
        nation = nation[0:nation.rfind('/')]

    start = '/dp/'
    end = '/'

    product_id = url[url.find(start)+len(start):url.rfind(end)]

    while (len(product_id) > 10):
        product_id = product_id[0:product_id.rfind(end)]

    REQUEST_URL = f'https://www.{DOMAIN}{nation}/gp/aod/ajax/ref=dp_aod_afts?asin={product_id}'

    # Get random header
    randIndex = randint(0, len(headers) - 1)
    cur_header = headers[randIndex]

    # Make the request
    future = session.get(REQUEST_URL, headers=cur_header)

    # Append to requests array
    reqs.append(future)

notified_products = [0] * len(reqs)

# Stock checker
def check_stock(notified_products, loop_count):

    successfull = 0
    failed = 0    
    i = 1

    for doc in as_completed(reqs):
        print(f'Checking the product #{i}')

        if (loop_count > 60):
            notified_products = [0] * len(reqs)

        in_stock = False

        if doc is not None:
            html = doc.result()

            cur_nation = ".com"

            if "amazon.co.uk" in html.url:
                cur_nation = ".co.uk"
            elif "amazon.com.tr" in html.url:
                cur_nation = ".com.tr"
            elif "amazon.de" in html.url:
                cur_nation = ".de"
            elif "amazon.es" in html.url:
                cur_nation = ".es"
            elif "amazon.com" in html.url:
                cur_nation = ".com"
            elif "amazon.it" in html.url:
                cur_nation = ".it"

            if html.status_code != 200:
                failed += 1
                print(html.status_code)
                print(html.url)
            else:
                successfull += 1

            # Scrap the web page
            soup = bs(html.content, 'html.parser')
            
            # DOM of stock diff's
            sold_by = soup.find(id="aod-offer-soldBy")
            amazon_seller = soup.find(text="Amazon")

            add_to_cart = soup.find_all(attrs={"name": "submit.addToCart"})

            if (add_to_cart != None):
                for element in add_to_cart:
                    if element.get('type') == 'submit':
                        if (sold_by != None):
                            seller = sold_by.get_text().lower()
                            if "amazon" in seller:
                                in_stock = True
                    else :
                        in_stock = False
            else:
                in_stock = False


            if sold_by != None:
                seller = sold_by.get_text().lower()
                if "amazon" in seller:
                    in_stock = True

            if (amazon_seller != None):
                in_stock = in_stock
            
            # Stock checker
            if (in_stock):
                cur_url = html.url

                cur_id = cur_url[cur_url.find('asin=')+len('asin='):]
                if (len(cur_id) > 10):
                    cur_id = cur_id[0:cur_id.rfind(end)]

                PRODUCT_PAGE = f'https://www.{DOMAIN}{cur_nation}/dp/{cur_id}/'

                # Update notified products
                notified_products[i - 1] += 1
                
                print(f'{i - 1} -> {notified_products[i-1]}')
                # Telegram BOT API
                if (notified_products[i - 1] < 3) :
                    data = {
                        'chat_id': CHAT_ID,
                        'text': f'{PRODUCT_PAGE} {PRODUCT_PAGE}',
                        'parse_mode': 'Markdown'
                    }
                    r = requests.post(TELEGRAM_API_SEND_MSG, data=data)

        i += 1
        loop_count += 1

    # Scraping Report
    if failed > 0:
        log  = f'{failed} of {failed + successfull} items has been failed during the scan!'
    else:
        log  = f'All {successfull} items has been scanned successfully!'

    # Telegram Message POST
    status = {
        'chat_id': BOTSTATUS_ID,
        'text': f'{log}',
        'parse_mode': 'Markdown'
    }
    c = requests.post(TELEGRAM_API_SEND_MSG2, data=status)

    # Connect to windscribe
    print("Reconnecting to Windscribe...")
    windscribe.connect(rand=True)  


# Run the program in a certain interval
while (True):
    check_stock(notified_products, loop_count)
    timer = randint(100, 300)
    time.sleep(timer)
    print("Rescanning starts...")