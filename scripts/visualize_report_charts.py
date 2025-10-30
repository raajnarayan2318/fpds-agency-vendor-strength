import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine

# -----------------------------
# 1️⃣ Database Connection
# -----------------------------
USERNAME = "raajthipparthy"
PASSWORD = "root"
HOST = "localhost"
PORT = "5432"
DATABASE = "fpds_project"

engine = create_engine(f"postgresql+psycopg2://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")

# -----------------------------
# 2️⃣ Tier Color Palette (same as report)
# -----------------------------
tier_colors = {
    "Elite": "#1a9850",         # Deep green
    "Core": "#66bd63",          # Medium green
    "Emerging": "#fee08b",      # Yellow
    "Prospect": "#fdae61",      # Orange
    "Dormant": "#d73027"        # Red
}
tier_order = ["Elite", "Core", "Emerging", "Prospect", "Dormant"]

# -----------------------------
# 3️⃣ Load Required Tables
# -----------------------------
scores = pd.read_sql("SELECT * FROM fpds.agency_contractor_scores;", engine)
tiers  = pd.read_sql("SELECT * FROM fpds.agency_contractor_tiers;", engine)
market = pd.read_sql("SELECT * FROM fpds.agency_market_12m;", engine)

print(f"✅ Loaded data: {len(scores)} vendor-agency rows, {len(tiers)} tiered entries")

# Merge tiers with scores for coloring
data = scores.merge(
    tiers[["vendor_key", "contracting_agency", "tier_label"]],
    on=["vendor_key", "contracting_agency"],
    how="left"
)

# -----------------------------
# 4️⃣ Chart 1: Relationship Score Distribution
# -----------------------------
plt.figure(figsize=(10, 6))
sns.histplot(data=data, x="relationship_score", hue="tier_label",
             bins=30, palette=tier_colors, multiple="stack", edgecolor="black")
plt.title("Distribution of Relationship Scores by Tier", fontsize=14, fontweight='bold')
plt.xlabel("Relationship Score (0–100)")
plt.ylabel("Vendor Count")
plt.legend(title="Tier", labels=tier_order)
plt.tight_layout()
plt.savefig("relationship_score_distribution.png", dpi=300)
plt.show()

# -----------------------------
# 5️⃣ Chart 2: Dollars vs Touches (Bubble = Tenure)
# -----------------------------
plt.figure(figsize=(10, 6))
sns.scatterplot(
    data=data,
    x="touches_12m",
    y="recent_dollars_12m",
    size="tenure_years",
    hue="tier_label",
    palette=tier_colors,
    alpha=0.7,
    sizes=(50, 500),
)

plt.yscale("log")  # Log scale because dollars vary widely
plt.title("Action Obligation vs Touches (Bubble = Tenure Years)", fontsize=14, fontweight='bold')
plt.xlabel("Touches in Past 12 Months")
plt.ylabel("Recent Dollars (log scale)")
plt.legend(title="Tier", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig("dollars_vs_touches_bubble.png", dpi=300)
plt.show()

# -----------------------------
# 6️⃣ Chart 3: Top 10 Agencies by Recent Dollars
# -----------------------------
top_agencies = market.sort_values("agency_recent_dollars_12m", ascending=False).head(10)

plt.figure(figsize=(10, 6))
sns.barplot(
    data=top_agencies,
    x="agency_recent_dollars_12m",
    y="contracting_agency",
    palette="Blues_r"
)
plt.title("Top 10 Agencies by Recent 12-Month Dollars", fontsize=14, fontweight='bold')
plt.xlabel("Recent 12-Month Dollars ($)")
plt.ylabel("Contracting Agency")
plt.tight_layout()
plt.savefig("top10_agencies_12m.png", dpi=300)
plt.show()

print("✅ Charts saved locally:")
print("   • relationship_score_distribution.png")
print("   • dollars_vs_touches_bubble.png")
print("   • top10_agencies_12m.png")