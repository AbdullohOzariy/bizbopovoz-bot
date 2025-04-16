import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

# Google Sheetsga ulanish
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
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
    data = sheet.col_values(4)[1:]  # D ustun: maktab nomlari
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
    top_school = labels[0]
    top_votes = counts[0]
    active_users = len(set(sheet.col_values(1)[1:]))

    # Ranglar
    colors = ['#388E3C' if s == top_school else '#64B5F6' for s in labels]

    # Grafik sozlamalari
    plt.figure(figsize=(12, 6), dpi=150)
    ax = plt.gca()
    ax.set_facecolor("#f9f9f9")

    bars = plt.bar(labels, counts, color=colors, edgecolor="#444", width=0.6)

    for bar, count in zip(bars, counts):
        percent = f"{(count / total_votes) * 100:.1f}%"
        label = f"{count} ta\n({percent})"
        plt.text(bar.get_x() + bar.get_width() / 2, count + 0.3, label,
                 ha='center', va='bottom', fontsize=9, fontweight='bold')

    # Sarlavha va izoh
    plt.title("📊 Maktablar bo‘yicha ovozlar statistikasi",
              fontsize=15, fontweight='bold', color="#222")

    plt.suptitle(f"🏆 Eng ko‘p ovoz olgan: {top_school} ({top_votes} ta)   |   Umumiy: {total_votes} ta ovoz",
                 fontsize=10, y=0.93, color="#555")

    # Faol foydalanuvchilar soni past burchakda
    plt.annotate(f"👤 Faol foydalanuvchilar: {active_users}",
                 xy=(1, 0.01), xycoords='axes fraction',
                 ha='right', va='bottom', fontsize=8, color="#777", alpha=0.75)

    # O‘qlar
    plt.xlabel("Maktablar", fontsize=11)
    plt.ylabel("Ovozlar soni", fontsize=11)
    plt.xticks(rotation=30, ha="right")
    plt.grid(axis="y", linestyle="--", linewidth=0.5, alpha=0.4)

    plt.tight_layout()
    plt.savefig(path, bbox_inches='tight')
    plt.close()
    return path
