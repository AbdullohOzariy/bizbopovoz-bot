import matplotlib.pyplot as plt

def generate_stats_chart(path="stats_chart.png"):
    stats = get_stats()
    labels = list(stats.keys())
    counts = list(stats.values())
    total = sum(counts)

    # Eng ko‘p ovoz olgan maktabni topish
    max_votes = max(counts)
    max_index = counts.index(max_votes)

    plt.figure(figsize=(14, 7))
    bars = plt.bar(labels, counts, color="#7ec8e3", edgecolor="black")

    # Eng ko‘p ovoz olgan barni yashilga bo‘yash
    bars[max_index].set_color("#74c476")

    for i, bar in enumerate(bars):
        height = bar.get_height()
        percentage = f"{(height / total) * 100:.1f}%"
        text = f"{int(height)} ta\n({percentage})"
        plt.text(bar.get_x() + bar.get_width()/2, height + 0.5, text,
                 ha='center', va='bottom', fontsize=11, fontweight='bold')

    plt.title("📊 Maktablar bo‘yicha ovozlar statistikasi", fontsize=16, fontweight='bold')
    plt.xlabel("Maktablar", fontsize=13)
    plt.ylabel("Ovozlar soni", fontsize=13)
    plt.xticks(rotation=30, ha='right', fontsize=11)
    plt.yticks(fontsize=11)
    plt.grid(axis='y', linestyle='--', linewidth=0.5, alpha=0.6)

    # Eng ko‘p ovoz haqida alohida matn
    max_label = labels[max_index]
    plt.figtext(0.5, 0.91, f"🏆 Eng ko‘p ovoz: {max_label} ({max_votes} ta)", ha='center', fontsize=12)
    plt.figtext(0.5, 0.89, f"👥 Umumiy ovozlar: {total}", ha='center', fontsize=10, color='gray')

    plt.tight_layout()
    plt.savefig(path)
    plt.close()
    return path
