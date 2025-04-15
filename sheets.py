import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Google Sheetsga ulanish
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

sheet = client.open("BizbopOvoz").worksheet("Votes")

def add_vote(name, surname, phone, school):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    sheet.append_row([name, surname, phone, school, now])

def get_stats():
    data = sheet.col_values(4)[1:]  # Maktab ustuni
    stats = {}
    for school in data:
        stats[school] = stats.get(school, 0) + 1
    return stats
def has_voted(phone):
    phone_column = sheet.col_values(3)[1:]  # Telefonlar ustuni (C)
    return phone in phone_column
