import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from scraper import (
    get_price_jarajto,
    get_price_vaporshop,
    get_price_vapefully,
    get_price_cbdremedium,
    get_price_konopnysklep,
    get_price_unikatowe
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

    headers = df.iloc[0, 1:]  # Nagłówki produktów (kolumny B →)
    fields = df.iloc[:, 0]    # Pola: Cena u nas, Link Vaporshop, itd.

    for col_index, product_name in enumerate(headers, start=1):
        data = df.iloc[:, col_index]
        values = {fields[row]: df.iat[row, col_index] for row in range(1, len(fields))}

        # Zbieranie linków i aktualnych danych
        our_url = values.get("Link JaraJTo", "")
        our_price = get_price_jarajto(our_url) if our_url else parse_price(values.get("Cena u nas"))

        if our_price:
            df.at[fields[2:].tolist().index("Cena u nas") + 1, col_index] = str(our_price)

        # Funkcja pomocnicza
        def try_update(link_label, price_label, scraper_func):
            link = values.get(link_label, "")
            if link and link.startswith("http"):
                try:
                    price = scraper_func(link)
                    if price:
                        df.at[fields[2:].tolist().index(price_label) + 1, col_index] = str(price)
                        return price
                except Exception as e:
                    print(f"[!] Błąd {link_label}:", e)
            return None

        # Pobierz ceny konkurencji
        konkurencyjne = [
            try_update("Link Vaporshop", "Cena Vaporshop", get_price_vaporshop),
            try_update("Link Vapefully", "Cena Vapefully", get_price_vapefully),
            try_update("Link CBDRemedium", "Cena CBDRemedium", get_price_cbdremedium),
            try_update("Link Konopnysklep", "Cena Konopnysklep", get_price_konopnysklep),
            try_update("Link Unikatowe", "Cena Unikatowe", get_price_unikatowe)
        ]
        konkurencyjne = [p for p in konkurencyjne if p is not None]

        # Wylicz status i działanie
        if our_price is not None and konkurencyjne:
            min_price = min(konkurencyjne)
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
