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

    price_rows = {
        "Cena u nas": 3,
        "Cena Vaporshop": 4,
        "Cena Vapefully": 5,
        "Cena CBDRemedium": 6,
        "Cena Konopnysklep": 7,
        "Cena MagicVapo": 8,
        "Cena Vapuj": 9,
        "Cena Unikatowe": 10
    }

    link_rows = {
        "Link JaraJTo": 11,
        "Link Vaporshop": 12,
        "Link Vapefully": 13,
        "Link CBDRemedium": 14,
        "Link Konopnysklep": 15,
        "Link MagicVapo": 16,
        "Link Vapuj": 17,
        "Link Unikatowe": 18
    }

    headers = df.iloc[0, 1:]
    fields = df.iloc[:, 0]

    for col_index, product_name in enumerate(headers, start=1):
        getval = lambda label: df.iat[link_rows[label], col_index] if label in link_rows and link_rows[label] < len(df) else ""
        our_link = getval("Link JaraJTo")
        our_price = get_price_jarajto(our_link) if our_link else parse_price(df.iat[price_rows["Cena u nas"], col_index])
        if our_price is not None:
            df.iat[price_rows["Cena u nas"], col_index] = our_price

        def try_update(label_link, label_price, scraper_func):
            link = getval(label_link)
            if link and link.startswith("http"):
                try:
                    price = scraper_func(link)
                    if price is not None:
                        df.iat[price_rows[label_price], col_index] = price
                        return price
                except Exception as e:
                    print(f"[!] Błąd przy {label_link}: {e}")
            return None

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

        if our_price is not None and competitor_prices:
            min_price = min(competitor_prices)
            dzialanie_row = fields[1:].tolist().index("Działanie") + 1
            status_row = fields[1:].tolist().index("Status") + 1

            dzialanie = round((min_price - 10) - our_price, 2)
            df.iat[dzialanie_row, col_index] = dzialanie

            # Wdrożona dokładna logika statusu:
            if dzialanie == 0:
                df.iat[status_row, col_index] = "✅ Mamy najtaniej"
            elif 0 < dzialanie <= 20:
                df.iat[status_row, col_index] = "⚠️ Można podnieść"
            elif dzialanie > 20:
                df.iat[status_row, col_index] = "💸 Za tanio"
            elif dzialanie < 0:
                df.iat[status_row, col_index] = "🔻 Można obniżyć"
        else:
            status_row = fields[1:].tolist().index("Status") + 1
            df.iat[status_row, col_index] = ""

    sheet.update(df.values.tolist())

if __name__ == "__main__":
    update_sheet()
