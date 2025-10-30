import pandas as pd
import numpy as np
from sqlalchemy import create_engine

# -----------------------------
# 0) DB connection
# -----------------------------
USERNAME = "raajthipparthy"       # change if needed
PASSWORD = "root"  # change if needed
HOST = "localhost"
PORT = "5432"
DATABASE = "fpds_project"

engine = create_engine(f"postgresql+psycopg2://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")

# -----------------------------
# 1) Load clean actions
# Needed columns (from actions_clean):
#   unique_entity_id, legal_business_name, contracting_agency,
#   date_signed (DATE), action_obligation (NUMERIC)
# -----------------------------
q = """
SELECT
  unique_entity_id,
  legal_business_name,
  contracting_agency AS contracting_agency,
  date_signed,
  action_obligation
FROM fpds.actions_clean
WHERE contracting_agency IS NOT NULL
  AND legal_business_name IS NOT NULL
  AND date_signed IS NOT NULL
  AND action_obligation IS NOT NULL;
"""
actions = pd.read_sql(q, engine)

# Convert date_signed to proper datetime type
actions["date_signed"] = pd.to_datetime(actions["date_signed"])

# Normalize types/casing just in case
actions["legal_business_name"] = actions["legal_business_name"].str.strip().str.upper()

# Build vendor_key: UEI else uppercase vendor name (report rule)
# (If UEI missing/blank, fallback)
def make_vendor_key(row):
    uei = (row["unique_entity_id"] or "").strip()
    if uei:
        return uei
    return row["legal_business_name"]

actions["vendor_key"] = actions.apply(make_vendor_key, axis=1)

# -----------------------------
# 2) Define time windows (report: 12m recent dollars/touches, 18m recency flag)
# -----------------------------
today = pd.Timestamp.today().normalize()
cut_12m = today - pd.DateOffset(months=12)
cut_18m = today - pd.DateOffset(months=18)

# -----------------------------
# 3) Aggregate to Agency × Vendor per report
#    - Recent Dollars 12m: sum of obligations with date_signed >= cut_12m
#    - Touches 12m: count of actions with date_signed >= cut_12m
#    - Tenure Years: (max(date_signed) - min(date_signed)) / 365.25
#    - Recent 18m Flag: any action with date_signed >= cut_18m
# -----------------------------
grp = actions.groupby(["contracting_agency", "vendor_key"], as_index=False)

def recent_sum(series_dates, series_vals, cutoff):
    mask = series_dates >= cutoff
    return series_vals[mask].sum()

def recent_count(series_dates, cutoff):
    return (series_dates >= cutoff).sum()

agg = (
    grp.apply(lambda g: pd.Series({
        "recent_dollars_12m": recent_sum(g["date_signed"], g["action_obligation"], cut_12m),
        "touches_12m": recent_count(g["date_signed"], cut_12m),
        "tenure_years": (g["date_signed"].max() - g["date_signed"].min()).days / 365.25,
        "recent_18m_flag": (g["date_signed"] >= cut_18m).any()
    }))
    .reset_index(drop=True)
)

# -----------------------------
# 4) Percentile ranks WITHIN EACH AGENCY with edge-case rules (report)
# Rules:
#   - If group size == 1 → rank = 0.00
#   - If all values identical or zero-only → rank = 0.50
#   - Else percentile rank (average method)
# -----------------------------
def within_agency_percentile(df, value_col):
    out = df.copy()
    # Handle edge cases per agency
    def rank_one_agency(sub):
        # If only one row in agency
        if len(sub) == 1:
            sub[f"rank_{value_col}"] = 0.00
            return sub

        vals = sub[value_col].fillna(0)
        # If all values identical (e.g., all zero)
        if (vals == vals.iloc[0]).all():
            sub[f"rank_{value_col}"] = 0.50
            return sub

        # Standard percentile rank (average ties)
        # rank(pct=True) gives 1..N / N so min>0; we want 0..1
        r = vals.rank(method="average", pct=True)
        sub[f"rank_{value_col}"] = (r - r.min()) / (r.max() - r.min()) if r.max() != r.min() else 0.50
        return sub

    out = out.groupby("contracting_agency", group_keys=False).apply(rank_one_agency)
    return out

agg = within_agency_percentile(agg, "recent_dollars_12m")
agg = within_agency_percentile(agg, "tenure_years")
agg = within_agency_percentile(agg, "touches_12m")

# Rename rank columns to report names
agg = agg.rename(columns={
    "rank_recent_dollars_12m": "rank_dollars",
    "rank_tenure_years": "rank_tenure",
    "rank_touches_12m": "rank_touches"
})

# Some groupby ops above may produce those exact names; ensure existence
if "rank_dollars" not in agg.columns:
    agg["rank_dollars"] = agg.pop("rank_recent_dollars_12m")
if "rank_tenure" not in agg.columns:
    agg["rank_tenure"] = agg.pop("rank_tenure_years")
if "rank_touches" not in agg.columns:
    agg["rank_touches"] = agg.pop("rank_touches_12m")

# -----------------------------
# 5) Relationship Score per report
# raw = 0.50*rank_dollars + 0.30*rank_tenure + 0.20*rank_touches
# if recent_18m_flag == False, raw *= 0.85
# score = round(100 * raw, 2)
# -----------------------------
raw = 0.50*agg["rank_dollars"] + 0.30*agg["rank_tenure"] + 0.20*agg["rank_touches"]
raw_adjusted = np.where(~agg["recent_18m_flag"].fillna(False), raw * 0.85, raw)
agg["relationship_score"] = (100 * raw_adjusted).round(2)

# -----------------------------
# 6) (Optional but helpful) bring back UEI/Vendor Name for readability
# We'll pick the "main" name/UEI by joining the most recent record per (agency, vendor_key)
# -----------------------------
# For each agency×vendor_key, choose the row with the latest date to fetch a representative name/UEI
idx = (
    actions.sort_values(["contracting_agency", "vendor_key", "date_signed"])
           .groupby(["contracting_agency", "vendor_key"], as_index=False)
           .tail(1)[["contracting_agency", "vendor_key", "unique_entity_id", "legal_business_name"]]
           .drop_duplicates(["contracting_agency", "vendor_key"])
)

scores = agg.merge(idx, on=["contracting_agency", "vendor_key"], how="left")

# Arrange columns exactly like the report’s "core columns"
scores = scores[[
    "unique_entity_id",
    "legal_business_name",
    "contracting_agency",
    "recent_dollars_12m",
    "touches_12m",
    "tenure_years",
    "recent_18m_flag",
    "rank_dollars",
    "rank_tenure",
    "rank_touches",
    "relationship_score",
    "vendor_key"
]]

# -----------------------------
# 7) Write to PostgreSQL: fpds.agency_contractor_scores
# -----------------------------
scores.to_sql("agency_contractor_scores", engine, schema="fpds", if_exists="replace", index=False)

print("✅ Created fpds.agency_contractor_scores with", len(scores), "rows.")