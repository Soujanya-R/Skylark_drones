import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import json
import os

def connect_sheet(sheet_name):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    # Load credentials from environment variable
    creds_json = os.environ.get("GOOGLE_CREDS_JSON")
    if not creds_json:
        raise ValueError("Set the GOOGLE_CREDS_JSON environment variable!")

    creds_dict = json.loads(creds_json)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)

    sheet = client.open(sheet_name)
    return sheet

def load_data(sheet, worksheet_name):
    ws = sheet.worksheet(worksheet_name)
    data = ws.get_all_records()
    df = pd.DataFrame(data)

    # Clean column names
    df.columns = df.columns.str.strip()

    return df, ws
