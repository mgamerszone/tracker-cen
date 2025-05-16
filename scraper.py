import requests
from bs4 import BeautifulSoup
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def extract_price(text):
    try:
        clean = re.sub(r"[\s\xa0\u00a0]", "", text)
        match = re.search(r"(\d+[\.,]?\d*)", clean)
        if match:
            return float(match.group(0).replace(",", "."))
    except:
        pass
    return None

def get_price_from_em_tag(url, class_name):
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")
    el = soup.find("em", class_=class_name)
    if el:
        return extract_price(el.text)
    return None

def get_price_from_span_content(url, class_name):
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")
    el = soup.find("span", class_=class_name)
    if el:
        return extract_price(el.text)
    return None

def get_price_from_div_content(url, class_name):
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")
    el = soup.find("div", class_=class_name)
    if el and el.has_attr("content"):
        return extract_price(el["content"])
    return None

def get_price_jarajto(url):
    return get_price_from_em_tag(url, "main-price")

def get_price_vaporshop(url):
    return get_price_from_span_content(url, "product-price current-price-value")

def get_price_vapefully(url):
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")
    prices = soup.select("span.woocommerce-Price-amount bdi")
    for el in prices:
        price = extract_price(el.text)
        if price and price > 0:
            return price
    return None

def get_price_cbdremedium(url):
    return get_price_from_em_tag(url, "main-price color")

def get_price_konopnysklep(url):
    return get_price_from_div_content(url, "current-price h2 mb-0 text-primary")

def get_price_unikatowe(url):
    return get_price_from_span_content(url, "price product-price")

def get_price_magicvapo(url):
    return get_price_from_span_content(url, "price")

def get_price_vapuj(url):
    return get_price_from_span_content(url, "price")
