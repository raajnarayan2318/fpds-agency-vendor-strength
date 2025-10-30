import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine

# -----------------------------
# 1️⃣ Connect to PostgreSQL
# -----------------------------
USERNAME = "raajthipparthy"
PASSWORD = "root"
HOST = "localhost"
PORT = "5432"
DATABASE = "fpds_project"

engine = create_engine(f"postgresql+psycopg2://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")

# -----------------------------
# 2️⃣ Load the tier summary table
# -----------------------------
df = pd.read_sql("SELECT * FROM fpds.agency_tier_summary;", engine)

print(f"✅ Loaded {len(df)} summary rows")

# -----------------------------
# 3️⃣ Define consistent tier color palette (as per report)
# -----------------------------
tier_colors = {
    "Elite": "#1a9850",         # Deep green
    "Core": "#66bd63",          # Medium green
    "Emerging": "#fee08b",      # Yellow
    "Prospect": "#fdae61",      # Orange
    "Dormant": "#d73027"        # Red
}

# Ensure tiers display in report order
tier_order = ["Elite", "Core", "Emerging", "Prospect", "Dormant"]

# -----------------------------
# 4️⃣ Stacked Bar: Vendor Count per Tier per Agency
# -----------------------------
pivot_counts = (
    df.pivot_table(index="contracting_agency", columns="tier_label", values="vendors", fill_value=0)
    [tier_order]
)

pivot_counts.plot(kind="bar", stacked=True, color=[tier_colors[t] for t in tier_order], figsize=(12, 6))

plt.title("Vendor Count per Tier per Agency", fontsize=14, fontweight='bold')
plt.xlabel("Contracting Agency")
plt.ylabel("Number of Vendors")
plt.xticks(rotation=45, ha="right")

# Add legend
plt.legend(title="Tier", bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()
plt.show()

# -----------------------------
# 5️⃣ Average Relationship Score per Tier
# -----------------------------
plt.figure(figsize=(8, 5))
sns.barplot(
    data=df,
    x="avg_score",
    y="tier_label",
    order=tier_order,
    palette=tier_colors
)

plt.title("Average Relationship Score by Tier", fontsize=14, fontweight='bold')
plt.xlabel("Average Relationship Score")
plt.ylabel("Tier")
plt.tight_layout()
plt.show()

# -----------------------------
# 6️⃣ Display a color legend for tiers
# -----------------------------
import matplotlib.patches as mpatches

legend_patches = [mpatches.Patch(color=color, label=tier) for tier, color in tier_colors.items()]

plt.figure(figsize=(6, 1))
plt.legend(handles=legend_patches, loc='center', ncol=len(tier_colors), frameon=False)
plt.axis('off')
plt.title("Tier Color Legend", fontsize=12, fontweight='bold')
plt.tight_layout()
plt.show()