import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

# Google Sheetsga ulanish
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

sheet = client.open("BizbopOvoz").worksheet("Votes")

def has_voted(user_id):
    ids = sheet.col_values(1)[1:]  # A ustun: user_id
    return str(user_id) in ids

def add_vote(name, phone, school, user_id):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    sheet.append_row([str(user_id), name, phone, school, now])

def get_stats():
    data = sheet.col_values(4)[1:]  # D ustun: Maktab
    stats = {}
    for school in data:
        stats[school] = stats.get(school, 0) + 1
    return stats

def generate_stats_chart(path="stats_chart.png"):
    stats = get_stats()
    sorted_stats = dict(sorted(stats.items(), key=lambda x: x[1], reverse=True))
    labels = list(sorted_stats.keys())
    counts = list(sorted_stats.values())
    total_votes = sum(counts)
    top_school, top_votes = labels[0], counts[0]

    # Faol foydalanuvchilar soni (unique user_id)
    user_ids = sheet.col_values(1)[1:]
    active_users = len(set(user_ids))

    # Rangli ustunlar
    colors = plt.cm.Blues(np.linspace(0.5, 0.9, len(stats)))

    plt.figure(figsize=(12, 6))
    bars = plt.bar(labels, counts, color=colors, edgecolor="black")

    # Bar ustiga foiz va son yozuvi
    for bar, count in zip(bars, counts):
        percent = f"{(count / total_votes) * 100:.1f}%"
        plt.text(bar.get_x() + bar.get_width() / 2, count + 0.5,
                 f"{count} ({percent})", ha='center', va='bottom',
                 fontsize=9, fontweight='bold')

    # Sarlavha
    plt.title(f"🏆 Eng ko‘p ovoz: {top_school} ({top_votes} ta)", fontsize=14, fontweight='bold', color="#2E7D32")
    plt.suptitle(f"📊 Umumiy ovozlar soni: {total_votes}", fontsize=10, y=0.92, color='gray')

    # Pastki burchakka foydalanuvchilar soni
    plt.annotate(f"👤 Faol foydalanuvchilar: {active_users}",
                 xy=(1, 0), xycoords='axes fraction',
                 fontsize=7, color="gray", ha='right', va='bottom', alpha=0.6)

    plt.xlabel("Maktablar", fontsize=11)
    plt.ylabel("Ovozlar soni", fontsize=11)
    plt.xticks(rotation=30, ha="right")
    plt.grid(axis="y", linestyle="--", linewidth=0.5, alpha=0.5)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    return path
