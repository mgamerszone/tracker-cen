import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from scraper import (
    get_price_vaporshop,
    get_price_vapefully,
    get_price_cbdremedium,
    get_price_konopnysklep,
    get_price_unikatowe
)

SHEET_NAME = "Tracker cen z poprawionymi nazwami"
WORKSHEET_INDEX = 0

def authorize_gsheet(json_keyfile_path):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile_path, scope)
    client = gspread.authorize(creds)
    return client

def update_sheet():
    client = authorize_gsheet("credentials.json")
    sheet = client.open(SHEET_NAME).get_worksheet(WORKSHEET_INDEX)
    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    for i, row in df.iterrows():
        our_price = float(str(row["Cena u nas"]).replace(",", ".") or 0)

        def try_update(column_prefix, get_price_func):
            link = row.get(f"Link {column_prefix}")
            if link:
                try:
                    competitor_price = get_price_func(link)
                    df.at[i, f"Cena {column_prefix}"] = competitor_price
                    df.at[i, f"Różnica {column_prefix}"] = round(our_price - competitor_price, 2)
                except Exception as e:
                    print(f"Błąd przy {column_prefix}: {e}")

        try_update("Vaporshop", get_price_vaporshop)
        try_update("Vapefully", get_price_vapefully)
        try_update("CBDRemedium", get_price_cbdremedium)
        try_update("Konopnysklep", get_price_konopnysklep)
        try_update("Unikatowe", get_price_unikatowe)

        competitor_prices = [
            df.at[i, f"Cena {k}"] for k in ["Vaporshop", "Vapefully", "CBDRemedium", "Konopnysklep", "Unikatowe"]
            if df.at[i, f"Cena {k}"] != ""
        ]
        min_price = min([float(p) for p in competitor_prices], default=99999)
        if our_price > min_price:
            df.at[i, "Status"] = "Można obniżyć"
        else:
            df.at[i, "Status"] = "Mamy najtaniej"

    sheet.update([df.columns.values.tolist()] + df.values.tolist())

if __name__ == "__main__":
    update_sheet()
