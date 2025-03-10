import json
import requests
from lxml import html
import urllib3

PRICE_XPATH = "//table[contains(@class, 'text-center')]/tbody[@class='table-padding-lg']/tr[1]/td[2]"


def crawl_live(config_path):
    with open(config_path, "r") as f:
        config = json.load(f)
        URL = config["url"]
        TITLE = config["title"]


    default_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    }

    request_headers = default_headers.copy()

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    response = requests.get(
        URL, 
        headers=request_headers, 
        timeout=3, 
        verify=False
    )

    response.raise_for_status()

    tree = html.fromstring(response.content)

    tree.make_links_absolute(base_url=URL)

    price = tree.xpath(PRICE_XPATH)[0]
    price = price.text.replace(',', '')

    import pandas as pd
    import datetime

    data = {
        'id': [datetime.datetime.now().strftime("%Y%m%d%H%M%S")],
        'title': [TITLE],
        'price': [float(price)],
        'date': [datetime.date.today()],
        'datetime': [datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
    }
    return pd.DataFrame(data)