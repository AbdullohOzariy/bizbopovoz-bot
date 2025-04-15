# sheets.py

import os
import base64
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Faylni yo'qligini tekshirib, credentials.json ni yozamiz
if not os.path.exists("credentials.json") and "SHEETS_CREDENTIALS_JSON" in os.environ:
    with open("credentials.json", "wb") as f:
        f.write(base64.b64decode(os.environ["SHEETS_CREDENTIALS_JSON"]))

# Google Sheetsga ulanish
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("BizbopOvoz").worksheet("Votes")

def add_vote(name, surname, phone, school):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    sheet.append_row([name, surname, phone, school, now])

def get_stats():
    data = sheet.col_values(4)[1:]
    stats = {}
    for school in data:
        stats[school] = stats.get(school, 0) + 1
    return stats

def has_voted(phone):
    phone_column = sheet.col_values(3)[1:]
    return phone in phone_column
