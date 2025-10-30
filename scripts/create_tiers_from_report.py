import pandas as pd
from sqlalchemy import create_engine

# ---- DB connection ----
USERNAME = "raajthipparthy"
PASSWORD = "root"
HOST = "localhost"
PORT = "5432"
DATABASE = "fpds_project"

engine = create_engine(f"postgresql+psycopg2://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")

# ---- Load the scored table produced earlier ----
scores = pd.read_sql("SELECT * FROM fpds.agency_contractor_scores;", engine)

# Safety: ensure required columns exist
required_cols = {
    "contracting_agency", "vendor_key", "legal_business_name", "unique_entity_id",
    "recent_dollars_12m", "touches_12m", "tenure_years", "recent_18m_flag",
    "rank_dollars", "rank_tenure", "rank_touches", "relationship_score"
}
missing = required_cols - set(scores.columns)
if missing:
    raise ValueError(f"Missing required columns in fpds.agency_contractor_scores: {missing}")

# ---- Apply tier rules from the report ----
# Priority order matters: Dormant overrides everything if not recent.
def assign_tier(row):
    score = float(row["relationship_score"] or 0)
    recent = bool(row["recent_18m_flag"])
    touches = int(row["touches_12m"] or 0)

    if not recent:
        return "Dormant"
    if score >= 80:
        return "Elite"
    if 60 <= score < 80:
        return "Core"
    # Emerging per report: 40–60 OR (score < 60 and Touches ≥ 2)
    if (40 <= score < 60) or (score < 60 and touches >= 2):
        return "Emerging"
    # Prospect: score < 40 and recent
    return "Prospect"

tiered = scores.copy()
tiered["tier_label"] = tiered.apply(assign_tier, axis=1)

# Numeric tier rank for convenient sorting (1 best)
tier_order = {"Elite": 1, "Core": 2, "Emerging": 3, "Prospect": 4, "Dormant": 5}
tiered["tier_rank"] = tiered["tier_label"].map(tier_order)

# Keep a clean set of columns for the tiers table (matches report-driven fields)
cols = [
    "unique_entity_id", "legal_business_name", "vendor_key", "contracting_agency",
    "recent_dollars_12m", "touches_12m", "tenure_years", "recent_18m_flag",
    "rank_dollars", "rank_tenure", "rank_touches", "relationship_score",
    "tier_label", "tier_rank"
]
tiered = tiered[cols]

# ---- Write the tier table to PostgreSQL ----
tiered.to_sql("agency_contractor_tiers", engine, schema="fpds", if_exists="replace", index=False)

# Optional: a compact summary per agency × tier (handy for visuals)
summary = (
    tiered.groupby(["contracting_agency", "tier_label"], as_index=False)
          .agg(vendors=("vendor_key", "nunique"),
               avg_score=("relationship_score", "mean"),
               total_recent_dollars=("recent_dollars_12m", "sum"))
)
summary.to_sql("agency_tier_summary", engine, schema="fpds", if_exists="replace", index=False)

print("✅ Created:")
print("  • fpds.agency_contractor_tiers (exact report tiers)")
print("  • fpds.agency_tier_summary   (counts/avg/$$ per tier)")