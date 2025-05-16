import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from scraper import (
    get_price_jarajto,
    get_price_vaporshop,
    get_price_vapefully,
    get_price_cbdremedium,
    get_price_konopnysklep,
    get_price_unikatowe,
    get_price_magicvapo,
    get_price_vapuj
)

SHEET_NAME = "Tracker_cen_konkurencji"
WORKSHEET_INDEX = 0

def authorize_gsheet(json_keyfile_path):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile_path, scope)
    client = gspread.authorize(creds)
    return client

def parse_price(val):
    try:
        return float(str(val).replace(",", ".").strip())
    except:
        return None

def update_sheet():
    client = authorize_gsheet("credentials.json")
    sheet = client.open(SHEET_NAME).get_worksheet(WORKSHEET_INDEX)
    rows = sheet.get_all_values()
    df = pd.DataFrame(rows)

    # Indeksy wierszy licząc od 0
    price_rows = {
        "Cena u nas": 4,
        "Cena Vaporshop": 5,
        "Cena Vapefully": 6,
        "Cena CBDRemedium": 7,
        "Cena Konopnysklep": 8,
        "Cena Unikatowe": 9,
        "Cena MagicVapo": 10,
        "Cena Vapuj": 11
    }

    link_rows = {
        "Link JaraJTo": 12,
        "Link Vaporshop": 13,
        "Link Vapefully": 14,
        "Link CBDRemedium": 15,
        "Link Konopnysklep": 16,
        "Link Unikatowe": 17,
        "Link MagicVapo": 18,
        "Link Vapuj": 19
    }

    headers = df.iloc[0, 1:]  # Nagłówki produktów
    fields = df.iloc[:, 0]    # Wiersze nazw

    for col_index, product_name in enumerate(headers, start=1):
        # Pobierz linki
        getval = lambda label: df.iat[link_rows[label], col_index] if label in link_rows else ""
        our_link = getval("Link JaraJTo")
        our_price = get_price_jarajto(our_link) if our_link else parse_price(df.iat[price_rows["Cena u nas"], col_index])
        if our_price:
            df.iat[price_rows["Cena u nas"], col_index] = str(our_price)

        def try_update(label_link, label_price, scraper_func):
            link = getval(label_link)
            if link and link.startswith("http"):
                try:
                    price = scraper_func(link)
                    if price:
                        df.iat[price_rows[label_price], col_index] = str(price)
                        return price
                except Exception as e:
                    print(f"[!] Błąd przy {label_link}: {e}")
            return None

        # Pobieranie cen konkurencji
        competitor_prices = [
            try_update("Link Vaporshop", "Cena Vaporshop", get_price_vaporshop),
            try_update("Link Vapefully", "Cena Vapefully", get_price_vapefully),
            try_update("Link CBDRemedium", "Cena CBDRemedium", get_price_cbdremedium),
            try_update("Link Konopnysklep", "Cena Konopnysklep", get_price_konopnysklep),
            try_update("Link Unikatowe", "Cena Unikatowe", get_price_unikatowe),
            try_update("Link MagicVapo", "Cena MagicVapo", get_price_magicvapo),
            try_update("Link Vapuj", "Cena Vapuj", get_price_vapuj)
        ]
        competitor_prices = [p for p in competitor_prices if p is not None]

        # Aktualizacja statusu i działania
        if our_price is not None and competitor_prices:
            min_price = min(competitor_prices)
            status_row = fields[1:].tolist().index("Status") + 1
            dzialanie_row = fields[1:].tolist().index("Działanie") + 1

            if our_price > min_price:
                df.iat[status_row, col_index] = "Można obniżyć"
            else:
                df.iat[status_row, col_index] = "Mamy najtaniej"

            dzialanie = round((min_price - 10) - our_price, 2)
            df.iat[dzialanie_row, col_index] = str(dzialanie)

    sheet.update([df.columns.values.tolist()] + df.values.tolist())

if __name__ == "__main__":
    update_sheet()
