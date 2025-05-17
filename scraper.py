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
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # najpierw próbuj znaleźć cenę promocyjną
        promo = soup.select_one("p.price ins .woocommerce-Price-amount")
        if promo:
            text = promo.get_text()
        else:
            # jeżeli nie ma promo, weź zwykłą cenę
            normal = soup.select_one("p.price > .woocommerce-Price-amount")
            text = normal.get_text() if normal else ""

        return parse_price(text)
    except Exception as e:
        print(f"Błąd przy get_price_vapefully: {e}")
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
