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

SHEET_NAME = "Tracker_cen_konkurencji"
WORKSHEET_INDEX = 0

def authorize_gsheet(json_keyfile_path):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile_path, scope)
    client = gspread.authorize(creds)
    return client

def update_sheet():
    client = authorize_gsheet("credentials.json")
    sheet = client.open(SHEET_NAME).get_worksheet(WORKSHEET_INDEX)

    rows = sheet.get_all_values()
    headers = rows[0]
    df = pd.DataFrame(rows[1:], columns=headers)

    for i, row in df.iterrows():
        try:
            our_price = float(str(row["Cena u nas"]).replace(",", ".") or 0)

            def try_update(prefix, scraper_func):
                link_col = f"Link {prefix}"
                price_col = f"Cena {prefix}"
                diff_col = f"Różnica {prefix}"
                link = row.get(link_col)

                if link and link.startswith("http"):
                    try:
                        price = scraper_func(link)
                        if price:
                            df.at[i, price_col] = str(price)
                            df.at[i, diff_col] = str(round(our_price - price, 2))
                    except Exception as e:
                        print(f"Błąd pobierania {prefix}: {e}")

            try_update("Vaporshop", get_price_vaporshop)
            try_update("Vapefully", get_price_vapefully)
            try_update("CBDRemedium", get_price_cbdremedium)
            try_update("Konopnysklep", get_price_konopnysklep)
            try_update("Unikatowe", get_price_unikatowe)

            competitor_cols = ["Cena Vaporshop", "Cena Vapefully", "Cena CBDRemedium", "Cena Konopnysklep", "Cena Unikatowe"]
            prices = [float(str(df.at[i, col]).replace(",", "."))
                      for col in competitor_cols if df.at[i, col].strip() != ""]
            min_price = min(prices) if prices else None

            if min_price and our_price > min_price:
                df.at[i, "Status"] = "Można obniżyć"
            elif min_price:
                df.at[i, "Status"] = "Mamy najtaniej"
            else:
                df.at[i, "Status"] = ""

        except Exception as e:
            print(f"Błąd w wierszu {i + 2}: {e}")

    sheet.update([df.columns.values.tolist()] + df.values.tolist())

if __name__ == "__main__":
    update_sheet()
