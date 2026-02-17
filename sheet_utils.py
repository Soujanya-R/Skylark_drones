import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

def connect_sheet(sheet_name):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "credentials.json", scope
    )

    client = gspread.authorize(creds)
    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1k3oq9NAW-X-gnMYclA68R7qPzB7XRSCU4CV9VeeZCxM/edit?gid=1597532669#gid=1597532669")


    return sheet


def load_data(sheet, worksheet_name):
    ws = sheet.worksheet(worksheet_name)
    data = ws.get_all_records()
    df = pd.DataFrame(data)

    # Clean column names
    df.columns = df.columns.str.strip()

    return df, ws

