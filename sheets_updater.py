import gspread
from oauth2client.service_account import ServiceAccountCredentials

def authorize_gsheet(json_keyfile_path):
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile_path, scope)
    client = gspread.authorize(creds)
    return client
