import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine

# -----------------------------
# 1️⃣  Connect to PostgreSQL
# -----------------------------
username = "postgres"         # change if needed
password = "your_password"    # same one you use in DBeaver
host = "localhost"
port = "5432"
database = "fpds_project"

connection_string = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"
engine = create_engine(connection_string)

# -----------------------------
# 2️⃣  Query summarized data
# -----------------------------
query = """
SELECT
    contracting_agency,
    SUM(action_obligation) AS total_obligation
FROM fpds.actions_clean
GROUP BY contracting_agency
ORDER BY total_obligation DESC
LIMIT 10;
"""
df = pd.read_sql(query, engine)
print("✅ Top 10 agencies by total obligation:")
print(df)

# -----------------------------
# 3️⃣  Create a simple bar chart
# -----------------------------
plt.figure(figsize=(10,6))
sns.barplot(x="total_obligation", y="contracting_agency", data=df, palette="Blues_r")
plt.title("Top 10 Contracting Agencies by Total Obligations")
plt.xlabel("Total Obligation ($)")
plt.ylabel("Contracting Agency")
plt.tight_layout()

# Save and show chart
plt.savefig("top10_agencies.png", dpi=300)
plt.show()

# ============================TOTAL OBLIGATIONS BY STATE=============================
# Obligations by State
query_state = """
SELECT entity_state, SUM(action_obligation) AS total_obligation
FROM fpds.actions_clean
WHERE entity_state IS NOT NULL
GROUP BY entity_state
ORDER BY total_obligation DESC
LIMIT 15;
"""
df_state = pd.read_sql(query_state, engine)

plt.figure(figsize=(10,6))
sns.barplot(x="total_obligation", y="entity_state", data=df_state, palette="Greens_r")
plt.title("Top 15 States by Contract Obligations")
plt.xlabel("Total Obligation ($)")
plt.ylabel("State")
plt.tight_layout()
plt.savefig("top15_states.png", dpi=300)
plt.show()