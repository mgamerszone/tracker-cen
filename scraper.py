import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def get_price_vaporshop(url):
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")
    price = soup.find("span", class_="product-price current-price-value")
    return float(price["content"]) if price else None

def get_price_vapefully(url):
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")
    el = soup.select_one("span.woocommerce-Price-amount bdi")
    if el:
        price = el.text.strip().split()[0].replace(",", ".")
        return float(price)
    return None

def get_price_cbdremedium(url):
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")
    el = soup.find("em", class_="main-price color")
    if el:
        price = el.text.strip().split()[0].replace(",", ".")
        return float(price)
    return None

def get_price_konopnysklep(url):
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")
    el = soup.find("div", class_="current-price h2 mb-0 text-primary")
    if el and "content" in el.attrs:
        return float(el["content"])
    return None

def get_price_unikatowe(url):
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")
    el = soup.find("span", class_="price product-price")
    if el and "content" in el.attrs:
        return float(el["content"])
    return None
