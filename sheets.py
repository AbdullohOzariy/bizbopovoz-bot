# sheets.py

import os
import base64
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

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

def generate_stats_chart(path="stats_chart.png"):
    stats = get_stats()
    labels = list(stats.keys())
    counts = list(stats.values())

    total_votes = sum(counts)

    plt.figure(figsize=(12, 6))
    bars = plt.bar(labels, counts, color="#4F9EC4", edgecolor="black")

    # Har bir bar ustiga qiymat yozish
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, height + 0.3, str(height),
                 ha='center', va='bottom', fontsize=10, fontweight='bold')

    plt.title("📊 Maktablar bo‘yicha ovozlar statistikasi", fontsize=14, fontweight='bold')
    plt.suptitle(f"Umumiy ovozlar soni: {total_votes}", fontsize=10, y=0.92, color='gray')

    plt.xlabel("Maktablar", fontsize=12)
    plt.ylabel("Ovozlar soni", fontsize=12)
    plt.xticks(rotation=30, ha="right")
    plt.grid(axis="y", linestyle="--", linewidth=0.5, alpha=0.7)
    plt.tight_layout()

    plt.savefig(path)
    plt.close()
    return path

